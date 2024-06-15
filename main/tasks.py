import datetime

import requests
import json
# import pprint
# from celery.schedules import crontab
from celery.utils.log import get_task_logger
from celery import (shared_task, )
# from deviare.celery import app
from django.db.models import Q
from .models import (Course, UserSettings, CourseLicenseUser, UserReport,
                     GCIndexAssessment, GCIndexReport)
from .serializers import CourseSerializer
from requests.auth import HTTPBasicAuth
from .utils import bulk_upsert
# from django.http import HttpResponseRedirect
# from django.contrib.auth import get_user_model
# from deviare import settings as deviare_settings

from .utils import add_user_to_course, usersignup
# from .authhelper import get_signin_url
# from django.urls import reverse

from .utils import get_link
import pandas as pd
import numpy as np
from django.db import transaction
from django.utils import timezone

logger = get_task_logger(__name__)
API_KEY = "iCSYT65KEBXPKIGj4qtrSJyx3Y5clM"
URL_ADDRESS = "https://deviare.talentlms.com/api/v1"

GCINDEX_API_KEY = 'e837722869ab72e624667648e5da7f5c'
GCINDEX_API_URL = "https://gcindex.eg1.co.uk/api.php"
url = f"{GCINDEX_API_URL}?key={GCINDEX_API_KEY}"


def gcapi(**kw):
    payload = {
        "action": "fetch"
    }
    payload.update({k: v for k, v in kw.items() if k in ['action', 'token']})
    headers = {
        'Content-Type': 'application/json'
    }
    query = requests.get
    if payload.get('action') in ['create', 'delete']:
        query = requests.post

    return query(url, headers=headers, data=json.dumps(payload))




def change_user_status_to_inactive(self, *args, user_id):
    """
    Update user profile on talent lms
    """
    try:

        url = "%s/usersetstatus/user_id:"+user_id+",status:inactive" % URL_ADDRESS
        response = requests.request("POST", url, auth=(API_KEY, ""), headers={}, files=[])
        if response.status_code == 200:
            logger.info("User Inactive"+user_id)
        else:
            logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)





def change_user_status_to_active(self, *args, user_id):
    """
    Update user profile on talent lms
    """
    try:

        url = "%s/usersetstatus/user_id:"+user_id+",status:active" % URL_ADDRESS
        response = requests.request("POST", url, auth=(API_KEY, ""), headers={}, files=[])
        if response.status_code == 200:
            logger.info("User Inactive"+user_id)
        else:
            logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)


@shared_task(name="create_course_on_talent_lms", bind=True)
def create_course_on_talent_lms(self, pk=None):
    """
    Post course content to Talent LMS
    """
    try:
        url = "%s/createcourse" % URL_ADDRESS

        course = Course.objects.get(pk=pk)
        serializer = CourseSerializer(course)

        content = serializer.data
        # Field values required to create a course on talentLMS
        course_creation_keys = {
            "name",
            "description",
            "code",
            "price",
            "time_limit",
            "category_id",
            "creator_id",
        }

        payload = {c: content[c] for c in content.keys() & course_creation_keys}

        files = []
        headers = {}

        response = requests.request(
            "POST",
            url,
            auth=HTTPBasicAuth(API_KEY, ""),
            headers=headers,
            data=payload,
            files=files,
        )

        logger.info(response.text.encode("utf8"))

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True, name="get_all_courses_from_talent_lms")
def get_all_courses_from_talent_lms(self):
    """
    Periodic task. Retrieve all course content from
    talent lms platform
    """
    try:

        url = "%s/courses" % URL_ADDRESS
        payload = {}
        headers = {}
        requests.post("https://webhook.site/3479bf16-ff7a-432e-aef6-76b7f238efb6", headers=headers,
                      data={"name": "alex"})
        response = requests.request("GET", url, auth=(API_KEY, ""), headers=headers, data=payload)

        # List of registered courses on talent lms
        if response.status_code == 200:
            content = json.loads(response.text)
            df = pd.DataFrame(content)
            if not df.empty:
                cols = list(set(df.columns.tolist()).intersection({c.name for c in Course._meta.get_fields()}))
                print(cols)
                cols.append('id')
                content = df[cols].to_dict(orient='records')
                bulk_upsert(content)

        else:
            logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)
        self.retry(exc=exc)


@shared_task(bind=True, name="assign_user_to_course")
def assign_user_to_course_on_talent_lms(self, *args, **kwargs):
    """
    Add user to course on talent LMS platform
    """

    try:
        for course in kwargs["courses"]:
            course_uuid = course["course_id"]
            users = [user["uuid"] for user in course["user"]]
            if users:
                assigned = CourseLicenseUser.objects.filter(
                    user_id__in=users, course_license_id__course_id=course_uuid
                )

                # By the time task runs, this objects would
                # have already been deleted
                unassigned = CourseLicenseUser.objects.filter(user_id__in=users).exclude(user_id__in=users)
                for entry in assigned:
                    # Retrieve identifiers provided by talent LMS
                    course_id = entry.course_license_id.course_id.course_id_talent_lms
                    user_id = entry.user_id.user_id_talentlms

                    if course_id:
                        if not user_id:
                            user = usersignup(entry.user_id)
                            user_id = user.user_id_talentlms
                        if user_id:
                            response = add_user_to_course(course_id=course_id, user_id=user_id)
                            if response is not None:
                                if response.status_code == 200:
                                    logger.info("User successfully assigned to course")
                                else:
                                    logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True, name="add_user")
def add_user_to_talent_lms(self, *args, **kwargs):
    """
    Add user to talent LMS
    """

    try:
        url = "%s/usersignup" % URL_ADDRESS
        payload = {
            "first_name": kwargs["firstName"],
            "last_name": kwargs["lastName"],
            "email": 'dnedit__' + kwargs["email"],
            "login": kwargs["userName"],
            "password": kwargs.get("unencrypted_password", "icecream1781"),
        }
        files = []
        headers = {}

        response = requests.request(
            "POST",
            url,
            auth=HTTPBasicAuth(API_KEY, ""),
            headers=headers,
            data=payload,
            files=files,
        )

        if response.status_code == 200:
            # User successfully created on TalentLMS
            content = json.loads(response.text)
            user = UserSettings.objects.get(email=kwargs["email"])
            user.user_id_talentlms = content["id"]
            user.save()

        else:
            logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True)
def edit_user_profile_on_talent_lms(self, *args, **kwargs):
    """
    Update user profile on talent lms
    """
    try:

        url = "%s/edituser" % URL_ADDRESS
        user_id = kwargs.get("user_id")
        password = kwargs.get("password")
        if user_id and password:

            payload = {"user_id": user_id, "password": password}

            response = requests.request("POST", url, auth=(API_KEY, ""), headers={}, data=payload, files=[])

            if response.status_code == 200:
                logger.info("password reset")

            else:
                logger.critical(response.text)

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True, name="retrieve_reports_from_mail")
def get_user_reports_from_mail(self):
    """
    Retrieve SimpliLearn user reports from
    mail server
    """

    try:

        link = get_link()
        logger.info(link)
        if not link:
            raise Exception

        df = pd.read_csv(link, low_memory=False)
        df = df.replace(to_replace="Not Assigned", value=np.nan)
        df = df.dropna(axis="columns", how="all")

        entries = CourseLicenseUser.objects.all().values(
            "user_id__email", "course_license_id__course_id__course_id")

        user_courses = []
        for e in list(entries):
            email = e["user_id__email"]
            val = e["course_license_id__course_id__course_id"]
            if not val:
                val = "-1"

            c = email + val
            user_courses.append(c)

        # Filter reports with existing course user license
        # information
        df["user_course"] = df["Learner Email"] + df["Course Id"].astype(str)
        df = df[df.user_course.isin(user_courses)]
        report = df.drop(columns=["user_course"])

        results = []
        for index, entry in report.iterrows():
            row = entry.dropna()
            # Drop columns and rows with unavailable data
            results.append(row.to_dict())

        duplicate_licences = []
        with transaction.atomic():
            for entry in results:
                email = entry["Learner Email"]
                course_id = entry["Course Id"]

                try:
                    course_completion = float(entry["Self-Learning Completion %"])
                    cl = CourseLicenseUser.objects.get(
                        user_id__email=email, course_license_id__course_id__course_id=course_id
                    )
                    cl.course_completion = course_completion
                    cl.save()

                    UserReport.objects.update_or_create(user_license=cl, defaults={"report": entry})

                except CourseLicenseUser.MultipleObjectsReturned:
                    duplicate_licences.append(cl.pk)
                    pass

                except Exception as e:
                    logger.exception(e)
                    raise

        logger.info("Duplicate licenses")
        logger.info(duplicate_licences)

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True, name="retrieve_reports_from_lms")
def get_user_course_report_on_talent_lms(self):
    try:
        # Get course licenses where provider is talent lms
        course_licenses = CourseLicenseUser.objects.select_related("course_license_id", "user_id").filter(
            course_license_id__course_id__course_id_talent_lms__isnull=False
        )

        for course_license in course_licenses:
            course_id = course_license.course_license_id.course_id.course_id_talent_lms
            user_id = course_license.user_id.user_id_talentlms

            url = "%s/getuserstatusincourse/course_id:%s,user_id:%s" % (URL_ADDRESS, course_id, user_id)

            try:
                response = requests.request("GET", url, auth=(API_KEY, ""), headers={}, data={}, files=[])
                if response.status_code == 200:
                    # Update user report information
                    entry = json.loads(response.text)
                    entry["provider"] = "devaire_talent_lms"

                    course_license.course_completion = entry["completion_percentage"]
                    course_license.save()

                    UserReport.objects.update_or_create(user_license=course_license, defaults={"report": entry})

            except Exception as exc:
                logger.exception(exc)
                continue

    except Exception as exc:
        logger.exception(exc)


@shared_task(bind=True, name="create_gcindex_token")
def create_gcindex_token(self, *args, **kwargs):
    import time
    try:
        url = f"{GCINDEX_API_URL}?key={GCINDEX_API_KEY}"
        t = time.time()
        assessment = GCIndexAssessment.objects.get(pk=kwargs.get('uuid'))
        payload = {
            "action": "create",
            "first_name": assessment.user.firstName,
            "last_name": assessment.user.lastName,
            "email": assessment.user.email
        }
        headers = {
            'Content-Type': 'application/json'
        }
        n = time.time()
        print(n - t)
        print(url, headers, payload)

        response = requests.post(url, headers=headers, data=json.dumps(payload))
        t = time.time()
        print(t - n)
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False) is not False:
                if assessment.token is None:
                    assessment.token = result.get('token')
                    assessment.save()
            n = time.time()
            print(n - t)
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="report_gcindex")
def report_gcindex(self, *args, **kwargs):
    from base64 import b64decode
    try:
        gc = GCIndexAssessment.objects.get(uuid=kwargs.get('uuid'))
        resp = gcapi(action='report', token=gc.token)
        if resp.ok:
            r = resp.json()

            if r and r.get('success', False):
                gcreport = GCIndexReport.objects.create(
                    assessment=gc,
                    report=b64decode(r['data']),
                    report_data=dict(base64=r['data'], type=r['type']))
                gc.state_id = 9
                gc.save()
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="delete_gcindex_token")
def delete_gcindex_token(self, *args, **kwargs):
    try:
        resp = gcapi(action='delete', token=kwargs.get('token'))
        if resp.ok:
            r = resp.json()
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="fetch_gcindex_single")
def fetch_gcindex_single(self, *args, **kwargs):
    try:
        logger.info('fetch_gcindex_single')
        url = f"{GCINDEX_API_URL}?key={GCINDEX_API_KEY}"
        assessment = GCIndexAssessment.objects.get(pk=kwargs.get('uuid'))
        payload = {
            "action": "fetch",
            "token": assessment.token,
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()

            if result.get('success', False) is not False:
                if assessment.token is None:
                    create_gcindex_token.apply_async(kwargs={'uuid': assessment.pk})
                else:
                    token_data = result.get('token')
                    for k in [
                        "completed",
                        "completed_at",
                        "has_report",
                        "url"
                    ]:
                        v = token_data.get(k)
                        if k == "completed_at" and v:
                            v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M")
                        setattr(assessment, k, v)
                    # if assessment.completed and assessment.report.count() == 0:
                    #     report_gcindex.apply_async(kwargs={'uuid': assessment.pk})

                    assessment.save()
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="fetch_gcindex_report")
def fetch_gcindex_report(self, *args, **kwargs):
    try:
        logger.info('fetch_gcindex_report')
        url = f"{GCINDEX_API_URL}?key={GCINDEX_API_KEY}"
        assessment = GCIndexAssessment.objects.get(pk=kwargs.get('uuid'))
        payload = {
            "action": "report",
            "token": assessment.token,
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()

            if result.get('success', False) is not False:
                if assessment.token is None:
                    create_gcindex_token.apply_async(kwargs={'uuid': assessment.pk})
                else:
                    token_data = result.get('token')
                    for k in [
                        "completed",
                        "completed_at",
                        "has_report",
                        "url"
                    ]:
                        v = token_data.get(k)
                        if k == "completed_at" and v:
                            v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M")
                        setattr(assessment, k, v)
                    assessment.save()
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="fetch_all_gcindex")
def fetch_all_gcindex(self, *args, **kwargs):
    try:
        url = f"{GCINDEX_API_URL}?key={GCINDEX_API_KEY}"

        payload = {
            "action": "fetch"
        }
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.get(url, headers=headers, data=json.dumps(payload))
        # return response
        if response.status_code == 200:
            result = response.json()
            if result.get('success', False) is not False:

                for token in result.get('tokens'):
                    data = {}
                    for k in [
                        "completed",
                        "completed_at",
                        "has_report",
                        "url"
                    ]:
                        v = token.get(k)
                        if k == "completed_at" and v:
                            v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M")
                        data[k] = v
                    GCIndexAssessment.objects.update_or_create(token=token.get('token'), defaults=data)
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="create_all_gcindex_tokens")
def create_all_gcindex_tokens(self, *args, **kwargs):
    try:
        logger.info('create_all_gcindex_tokens')
        qs = GCIndexAssessment.objects.filter(
            ~Q(gcologist__isnull=True) & Q(token__isnull=True), deleted=False,
        ).values('uuid')
        for uid in qs:
            create_gcindex_token.apply_async(kwargs=uid)
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="fetch_all_gcindex_detail")
def fetch_all_gcindex_detail(self, *args, **kwargs):
    try:
        logger.info('fetch_all_gcindex_detail')
        qs = GCIndexAssessment.objects.filter(
            Q(gcologist__isnull=False) & Q(token__isnull=False) & (
                    Q(has_report=False) | Q(completed=False)
            ), deleted=False,
        ).values('uuid')
        for uid in qs:
            fetch_gcindex_single.apply_async(kwargs=uid)
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="fetch_all_gcindex_url")
def fetch_all_gcindex_url(self, *args, **kwargs):
    try:
        logger.info('fetch_all_gcindex_url')
        cqs = GCIndexAssessment.objects.filter(
            gcologist__isnull=False,
            token__isnull=True,
            deleted=False
        ).values('uuid')
        for uid in cqs:
            create_gcindex_token.apply_async(kwargs=uid)

        qs = GCIndexAssessment.objects.filter(
            gcologist__isnull=False,
            token__isnull=False,
            deleted=False,
            url__isnull=True
        ).values('uuid')
        for uid in qs:
            fetch_gcindex_single.apply_async(kwargs=uid)
        logger.info('report_gcindex')
        rqs = GCIndexAssessment.objects.filter(
            report__report__isnull=True,
            has_report=True,
            deleted=False,
            completed_at__lt=timezone.now() - datetime.timedelta(minutes=80)
        ).values('uuid')
        for uid in rqs:
            report_gcindex.apply_async(kwargs=uid)
    except Exception as e:
        logger.exception(e)


@shared_task(bind=True, name="run_email_queue")
def run_email_queue(self, ):
    from notification.models import EmailMessage
    from tools.email import send_wrapped_email
    from time import time
    from django.utils import timezone
    logger.info('run_email_queue')
    print('run_email_queue')
    qs = EmailMessage.objects.filter(
        sent=False,
        proc_id__isnull=True,
        # send_after__lte=timezone.now()
    )
    qs.update(proc_id=round(time()))

    for em in qs:
        try:
            em.send()
        except Exception as exc:
            logger.exception(exc)


def del_lms_user(email):
    from main.fixer import delete_keycloak_user
    url = "%s/users/email:%s" % (URL_ADDRESS, str(email))
    resp = requests.request("GET", url, auth=(API_KEY, ""), )
    print(resp.json())
    ret = {'del_lms': False, 'del_kc': False}
    if resp.status_code == 200:
        user_id = resp.json().get('id')
        delete_url = "%s/deleteuser" % URL_ADDRESS
        d = dict(user_id=str(user_id), permanent='yes')
        delresp = requests.request("POST", delete_url, auth=(API_KEY, ""), data=d)
        if delresp.status_code == 200:
            ret['del_lms'] = delresp.json()

    ret['del_kc'] = delete_keycloak_user(email=email)

    return ret


def set_lms_email(self, *args, **kwargs):
    from main.fixer import update_keycloak_user
    import traceback
    import time
    """
    Update user profile lastname to email on talent lms
    """
    try:

        lurl = "%s/edituser" % (URL_ADDRESS)
        old_email = kwargs.get("old_email", None)
        u = UserSettings.objects.get(email=old_email)
        user_id = u.user_id_talentlms
        email = kwargs.get("email", False)
        ren_u = UserSettings.objects.get(email=email)
        ren_auth = ren_u.user
        f_email = f'old_{email}'
        ren_u.userName = f_email
        ren_u.email = f_email
        ren_auth.username = f_email
        ren_auth.email = f_email
        done = {}
        if old_email:
            done = del_lms_user(email)
            # if not done:
            #     return
        if user_id and email:
            ren_auth.save()
            ren_u.save()
            payload = {
                "user_id": user_id,
                "login": email,
                "email": email,
                # 'last_name': email,
                # 'first_name': ','
            }
            time.sleep(2.0)
            response = requests.request("POST", lurl, auth=(API_KEY, ""), headers={}, data=payload, files=[])

            if response.status_code == 200:
                done['lms_upd'] = response.json()
                done['kc_upd'] = update_keycloak_user(old_email=old_email, email=email)
                logger.info("email changed")
            else:
                logger.critical(response.text)
                done['lms_upd_error'] = str(response.text)
            auth_user = u.user
            u.userName = email
            u.email = email
            auth_user.username = email
            auth_user.email = email
            u.save()
            auth_user.save()
            return done
    except Exception as exc:
        traceback.print_stack()
        done['error'] = str(exc)
        logger.exception(exc)
    return done


@shared_task(bind=True, name="check-orders")
def check_orders(self, ):
    from wp_api.wcapi import WcApi
    from wp_api.views import process_order
    api = WcApi()
    orders = api.orders.read(params={'per_page': '1000'})
    for o in orders:
        process_order(o)

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#    print('setup_periodic_tasks')
#    print(sender)
#    logger.info('setup_periodic_tasks')
#    logger.info(str(sender))
#    sender.add_periodic_task(
#       crontab(hour='*', minute=0),
#        fetch_all_gcindex_detail.s(),
#    )
#    sender.add_periodic_task(
#        crontab(minute='*'),
#        run_email_queue.s(),
#    )
