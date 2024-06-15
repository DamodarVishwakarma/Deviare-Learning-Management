from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Order
from main.models import User, UserSettings, Course, CourseLicenseUser, CourseLicense, Project
import json
from main.utils import randomString
from django.utils.dateparse import parse_datetime
from datetime import datetime
import re

REGEX_USERNAME_CHECK = re.compile(r'([A-Z\s]+)')
REGEX_ONLY_NUMBERS = re.compile(r'^(\d+)$')

def valid_username(s):
    return len(REGEX_USERNAME_CHECK.findall(s)) == 0


def create_keyadmin():
    from keycloak import keycloak_admin
    from deviare import settings as deviare_settings
    return keycloak_admin.KeycloakAdmin(
            server_url=deviare_settings.KEYCLOAK_URL,
            username=deviare_settings.KEYCLOAK_ADMINUSER,
            password=deviare_settings.KEYCLOAK_ADMINPASSWORD,
            realm_name=deviare_settings.KEYCLOAK_REALM,
        )


def create_keycloak_user(username=None, email='', password=None, keyadmin=None):
    if username is None:
        username =  email
    if password is None:
        password = randomString()
    if keyadmin is None:
        keyadmin = create_keyadmin()
    try:
        keyadmin.create_user(
            {
                "email": email,
                "enabled": True,
                "username": username,
                "credentials": [{"value": password, "type": "password"}],
                "realmRoles": ["user_default"],
            }
        )
    except Exception as e:
        print(e)
    return dict(username=username, email=email, password=password)


def create_user_from_billing(
        first_name="",
        last_name="",
        company="",
        
        address_1="",
        address_2="",
        city="",
        state="",
        postcode="",
        country="",
        email=None,
        phone=""
    ):
    uqs = UserSettings.objects.filter(email=email)
    if uqs.exists():
        return uqs.first(), False
    user_settings = UserSettings(
        location=f"{address_1}, {address_2}, {city}, {state}, {postcode}",
        firstName=first_name,
        lastName=last_name,
        email=email,
        userName=email,
        country=country,
        contact_no=phone,
        role='user'
    )

    user = User(
        first_name=first_name,
        last_name=last_name,
        email=email,
        username=email,
    )

    pwd = randomString()
    user.set_password(pwd)
    user_settings.set_password(pwd)
    keyadmin = create_keyadmin()
    keyadmin.create_user(
        {
            "email": user_settings.email,
            "username": user_settings.userName,
            "enabled": True,
            "firstName": user_settings.firstName,
            "lastName": user_settings.lastName,
            "credentials": [{"value": pwd, "type": "password"}],
        }
    )
    user.save()
    user_settings.user = user
    user_settings.save()
    return user_settings, pwd


def safe_int(s):
    try:
        return int(s)
    except Exception as e:
        pass
    return s


def parse_date(s=None):
    dformat = '%d/%m/%Y, %H:%M:%S'
    if s is None:
        return s
    try:
        if REGEX_ONLY_NUMBERS.findall(s):
            return datetime.fromtimestamp(safe_int(s))
        r = parse_datetime(s)
        if r:
            return r
        return datetime.strptime(s, dformat)
    except Exception as e:
        pass
    return s

    
LINE_ITEM_DEFAULTS = {
    "id": None,
    "product_id": 0,
    "variation_id": 0,
    "quantity": 0,
    "sku": None
}
ORDER_DEFAULTS = {
    "order_id": str,
    "number": str,
    "order_key": str,
    "customer_id": str,
    "customer_ip_address": str,
    "customer_user_agent": str,
    "customer_note": str,
   
   # "created_via": "",
    # "version": "3.0.0",#
    "status": str,
    "date_paid_gmt": parse_date,
    "date_completed_gmt": parse_date,
    "billing": json.dumps,
    "line_items": json.dumps
}


def get_website_project():
    return Project.objects.get(project_name='Deviare Website')


def process_line_item(user, sku=None, quantity='1', **kw):
    course = Course.objects.get(pk=sku)
    p = get_website_project()
    course_license, c = CourseLicense.objects.get_or_create(project_id=p, course_id=course, count=100000)
    if c:
        course_license.count = 100000
        course_license.save()
    else:
        CourseLicenseUser.objects.filter(course_license_id=course_license)
    lic_user, cl = CourseLicenseUser.objects.get_or_create(course_license_id=course_license, user_id=user)
    return {'course': str(lic_user), 'new_license': cl}


def send_order_complete_email(user, course_licenses, pwd=False):
    from django.core.mail import send_mail
    cou = "\n".join([c.get('course') for c in course_licenses])
    plural = 's' if len(course_licenses) > 1 else ''  
    ext = '' if pwd is False else f"""

Your login details are:
Username : {user.userName}
Password : {pwd}
    """ 
    body = f"""
Welcome {user.firstName} {user.lastName},

You have successfully been registered for the following courses:
{cou}

You can access the above course{plural} at:
https://platform-staging.deviare.co.za
{ext}

Thank you,
Deviare Support Team
    """
    send_mail(
        [user.email],
        "Deviare Login Details",
        body,
    )


def process_complete_order(o):
    if not o.sent_mail:
        line_items = json.loads(o.line_items)
        billing = json.loads(o.billing)
        user, pwd = create_user_from_billing(**billing)
        course_licenses = []
        for line in line_items:
            course_licenses.append(process_line_item(user, **line))
        #if pwd is not False:
        send_order_complete_email(user, course_licenses, pwd)
        o.sent_mail = True
        o.save()


def process_order(data=None):
    if data is None:
        return 
    status = data.get('status', None)
    complete_order = False
    if status is None:
        return
    orders = Order.objects.filter(order_id=data.get('id'))
    data['order_id'] = data.pop('id')
    if not orders.exists():
        o = Order(raw_data=json.dumps(data), **{k: mthd(data.get(k, None)) for k, mthd in ORDER_DEFAULTS.items()})
        complete_order = status == 'completed'
    else:
        o = orders.first()
        o.raw_data = json.dumps(data)
        complete_order = status == 'completed' and o.status != 'completed'
        for k, mthd in ORDER_DEFAULTS.items():
            setattr(o, k, mthd(data.get(k, None)))
    o.save()
    if complete_order:
         process_complete_order(o)


@api_view(['POST'])
def wc_hook(request):
    data = None
    if not hasattr(request, 'data'):
        try:
            data = json.loads(request.POST.body)
        except Exception as e:
            print(e)
            return Response(status=200)
    else:
        data = request.data
    if data is None:
        return Response(status=200)
    process_order(data)
    return Response(status=200)


