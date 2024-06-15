import base64
import random
import string
import requests
import logging
from django.db import connection
from .models import UserSettings, Course
from requests.auth import HTTPBasicAuth
from imaplib import IMAP4_SSL
from datetime import datetime, timedelta
import email
import re
import json
import pandas as pd
from deviare import settings as deviare_settings
import numpy as np
logger = logging.getLogger(__name__)

# TODO move to environment variables
API_KEY = "iCSYT65KEBXPKIGj4qtrSJyx3Y5clM"
URL_ADDRESS = "https://deviare.talentlms.com/api/v1"


def email_check(email):
    email = email.casefold()
    return True if UserSettings.objects.filter(email=email).exists() else False


def randomString(stringLength=8):
    characters = [c for c in list(list(string.ascii_letters) + list(string.digits))]
    return "".join([random.choice(characters) for i in range(stringLength)])


def return_image_extenstion(base64string):
    image_splits = base64string.split(";base64,")
    extension = image_splits[0].split("/").pop()
    data = base64.b64decode(image_splits[1])
    return data, extension


def sl_cron_job():

    from main.models import Course
    from main.serializers import CourseSerializer

    # Simplilearn API for course catalog
    courses_url = "https://services.simplilearn.com/enterprise-catalog/get-course-catalog?country_code=US"
    headers = {"Authorization": "Bearer 5c166aee943ce89c741ccd8e6b8400e5"}
    all_courses = requests.get(courses_url, headers=headers)
    data = all_courses.json().get("data")
    count = 0

    # Saving into database
    for course in data:
        count += 1
        print(count)

        # Setting Blanks to Master Programs
        if course["category"] == "":
            course["category"] = "Master Programs"

        course_data = {
            "name": course["course_name"],
            "description": course["description"],
            "provider": "SimpliLearn",
            "link": course["course_url"],
            "category": course["category"],
            "course_id": course["course_id"],
            "course_type": course["course_type"],
        }

        # Update
        if Course.objects.filter(course_id=course["course_id"], course_type=course["course_type"]).exists():
            course = Course.objects.filter(course_id=course["course_id"], course_type=course["course_type"]).first()
            serializer = CourseSerializer(course, data=course_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        # Save
        else:
            serializer = CourseSerializer(data=course_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

    print("Done")


def lookup_create():
    return {lookup_key(k): v for k, v in Course.objects.filter(course_id_talent_lms__isnull=True).values_list('name', 'category')}


HT = re.compile(r'<(.*?)>')
REG_NON_WORD = re.compile(r'(\s+|\W+)', re.I)
RAZ = re.compile(r'(azure|Cloud Computing)', re.I)


def clean_name(s):    
    return HT.sub('', s).encode('latin').replace(b'\xc3', b'').replace(b'\x82', b'').replace(b'\xc2', b' ').decode('latin')


def lookup_key(s):
    return REG_NON_WORD.sub('_', s.lower())


def bulk_upsert(courses):
    """
    Insert / Update course content from TalentLMS
    """

    try:        
        lookup = lookup_create()
        for course in courses:
            course_id_talent_lms = course.pop('id')
            name = course.get("name")
            course["course_id_talent_lms"] = course_id_talent_lms
            course["category"] = 'Cloud Computing' if RAZ.findall(name) else lookup.get(lookup_key(name), 'Misc')
            course["provider"] = "Talent LMS"
            course["name"] = f"LMS-{course_id_talent_lms} {name}"
            obj, created = Course.objects.update_or_create(course_id_talent_lms=course_id_talent_lms, defaults=course)

    except Exception as exc:
        logger.exception(exc)


def add_user_to_course(user_id=None, course_id=None, **kw):
    """
    Add user to course on talent LMS
    """
    try:
        payload = {"user_id": user_id, "course_id": course_id, "role": "learner"}

        url = "%s/addusertocourse" % (URL_ADDRESS)
        response = requests.request("POST", url, auth=HTTPBasicAuth(API_KEY, ""), headers={}, data=payload, files=[])

        return response

    except Exception as exc:
        logger.exception(exc)
        return None


def add_user(*args, **kwargs):
    """
    Add user to talentLMS
    """
    try:

        url = "%s/usersignup" % (URL_ADDRESS)
        response = requests.request("POST", url, auth=HTTPBasicAuth(API_KEY, ""), headers={}, data=kwargs, files=[])

        return response

    except Exception as exc:
        logger.exception(exc)
        return None


def get_talentlms_request():
    from lms.api import LmsRequestProxy
    return LmsRequestProxy()


def usersignup(user, branch_id=None):
    """
    Add user to talentLMS
    """

    try:
        if not isinstance(user, UserSettings):
            user_qs = UserSettings.objects.filter(pk=str(user))
            if user_qs.exists():
                user = user_qs.first()
        url = "usersignup"
        r = get_talentlms_request()
        response = r.post(
            url,
            data=dict(
                first_name=user.firstName,
                last_name=user.lastName,
                email='dnedit__'+user.email,
                login=user.userName,
                password="iceScream",
            )
        )
        if 'error' in response:
            err = response['error']
            if err['message'].find('already exists') != -1:
                em = err['message'].find('already exists')
                p = f'email:{user.email}' if em else f'username:{user.userName}'
                url = f'users/{p}'
                response = r.get(url)
                #return user
        if 'id' in response:
            user.user_id_talentlms = response["id"]
            user.save()
        return user
    except Exception as exc:
        logger.exception(exc)
        return None


def parse_email(message):
    """
    Parse email body to get href link
    """
    for part in message.walk():
        if part.get_content_type() == "text/html":
            content = part.get_payload()
            hrefs = re.findall(r'href=[\'"]?([^\'" >]+)', content)

            for href in hrefs:
                if "s3.amazonaws.com" in href:
                    return href

    return None


def get_link():
    """
    IMAP outlook authentication. Retrieve email body
    from simplilearn
    """
    
    MAIL_FROM = "noreply@simplilearn.training"
    SUBJECT = "Deviare Learner Activity"
    try:
        imap = IMAP4_SSL(host="outlook.office365.com", port=993)
        status, message = imap.login(
            user="noreply@deviare.co.za", password="Lam82139"
        )
        if status != "OK":
            raise Exception
        # We have been authed, select INBOX
        imap.select(mailbox="INBOX", readonly=True)

        date = datetime.now() - timedelta(days=7)
        # Partial match on subject header
        status, body = imap.search(
            None,
            '(FROM "%s")' % (MAIL_FROM),
            '(SUBJECT "%s")' % (SUBJECT),
            '(SINCE "%s")' % (date.strftime("%d-%b-%Y")),
        )
        if status != "OK":
            raise Exception

        # Assuming we only receive one email in time period
        identifier = body[0]

        status, body = imap.fetch(identifier, "(RFC822)")
        if status != "OK":
            raise Exception

        message = email.message_from_bytes(body[0][1])

        link = parse_email(message)
        imap.close()

        return link

    except Exception as exc:
        logger.exception(exc)
        return None


def to_secs(value):
    try:
        print(value)
        return pd.Timedelta(value).total_seconds() if str(value).find('None') == -1 and type(value) not in (
            None, False, np.infty, np.NaN, pd.NaT) else 0
    except ValueError as ve:
        return 0


def read_uri(url):
    import mimetypes
    from urllib.parse import urlparse
    from os.path import exists
    mime, n = mimetypes.guess_type(url)
    p = urlparse(url)
    if p.netloc == '':
        if exists(url):
            with open(url, 'rb') as f:
                data = f.read()
    else:
        r = requests.get(url)
        if r.ok:
            data = r.content
    return mime, data, p.path


def image_from(fn):
    mime, data, rn = read_uri(fn)
    bdata = base64.b64encode(data).decode('utf-8')
    if data:
        return f'data:{mime};base64,{bdata}'
    else:
        return fn


# def get