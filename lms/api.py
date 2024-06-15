from requests import Request, Session, request
from requests.auth import HTTPBasicAuth
from django.conf import settings

from lms.models import *

LMS_API_KEY = getattr(settings, "LMS_API_KEY", 'iCSYT65KEBXPKIGj4qtrSJyx3Y5clM')
LMS_API_URL = getattr(settings, "LMS_API_URL", 'https://deviare.talentlms.com/api')
LMS_API_VERSION = getattr(settings, "LMS_API_VERSION", "v1")


def params_serialize(**kw):
    return ','.join(["{}:{}".format(k, v) for k, v in kw.items()])


class LmsRequestProxy(object):
    def __init__(self):
        self._base_url = f'{LMS_API_URL}/{LMS_API_VERSION}/%s'
        # self._session = Session()
        # self._req = Request('GET',
        # f'{LMS_API_URL}/{LMS_API_VERSION}/%s',
        # auth=HTTPBasicAuth(LMS_API_KEY, ""), **kwargs)
        # self._prepped = self._session.prepare_request(self._req)

    def _handle_response(self, resp):
        if resp.ok:
            if resp.headers['content-type'].find('application/json') != -1:
                return resp.json()
        return None

    def request(self, method='GET', url='users',  **kwargs):
        return request(
            method,
            self._base_url % url,
            auth=HTTPBasicAuth(LMS_API_KEY, ""), **kwargs)

    def post(self, url, **kwargs):

        resp = self.request(method='POST', url=url, **kwargs)
        print(self._base_url % url, resp.json())
        return resp.json()

    def get(self, url, **kwargs):
        resp = self._handle_response(self.request(url=url, **kwargs))
        return resp


class LmsUserProxy(object):
    pass


class Collection(object):
    def __init__(self, name='course', children=['group', 'user', 'unit'], parents=['branch', 'group']):
        self._base = name
    """
    
    {"url": "categories", "params": "id:1", "method": "GET"},
    {"url": "buycategorycourses", "params": "", "method": "POST"},
    {"url": "buycourse", "params": "", "method": "POST"},
    {"url": "categoryleafsandcourses", "params": "id:1", "method": "GET"},
    
    
    {"url": "branches", "params": "id:1", "method": "GET"},
    {"url": "createbranch", "params": "", "method": "POST"},
    {"url": "deletebranch", "params": "", "method": "GET"},
    {"url": "branchsetstatus", "params": "branch_id:73,status:active", "method": "GET"},
    
    
    {"url": "courses", "params": "id:1", "method": "GET"},
    {"url": "createcourse", "params": "", "method": "POST"},
    {"url": "deletecourse", "params": "", "method": "GET"},
    
    {"url": "getcustomcoursefields", "params": "", "method": "GET"},
    {"url": "getcoursesbycustomfield", "params": "custom_field_value:test", "method": "GET"},
    
    {"url": "getiltsessions", "params": "ilt_id:1", "method": "GET"},
    
    {"url": "addcoursetogroup", "params": "course_id:1,group_id:1", "method": "GET"},
    {"url": "addcoursetobranch", "params": "course_id:1,branch_id:1", "method": "GET"},
    
    
    {"url": "groups", "params": "id:1", "method": "GET"},
    {"url": "creategroup", "params": "", "method": "POST"},
    {"url": "deletegroup", "params": "", "method": "GET"},
    
    
    {"url": "siteinfo", "params": "", "method": "GET"},
    {"url": "ratelimit", "params": "", "method": "GET"},
    
    {"url": "users", "params": "email:example@example.com", "method": "GET"},
    {"url": "users", "params": "id:1", "method": "GET"},
    {"url": "usersignup", "params": "", "method": "POST"},
    {"url": "edituser", "params": "", "method": "POST"},
    {"url": "usersetstatus", "params": "user_id:71,status:inactive", "method": "GET"},
    {"url": "deleteuser", "params": "", "method": "GET"},
    
    {"url": "addusertocourse", "params": "", "method": "GET"},
    {"url": "removeuserfromcourse", "params": "user_id:1,course_id:1", "method": "GET"},
    
    {"url": "removeuserfromgroup", "params": "user_id:1,group_id:1", "method": "GET"},
    {"url": "addusertogroup", "params": "user_id:1,group_key:1", "method": "GET"},
    
    {"url": "removeuserfrombranch", "params": "user_id:1,branch_id:1", "method": "GET"},
    {"url": "addusertobranch", "params": "user_id:1,branch_id:1", "method": "GET"},
    
    
    {"url": "gotocourse", "params": "user_id:1,course_id:127,course_completed_redirect:google.com,logout_redirect:google.com", "method": "GET"},
    
    {"url": "gettestanswers", "params": "test_id:1,user_id:1", "method": "GET"},
    {"url": "getsurveyanswers", "params": "survey_id:1,user_id:1", "method": "GET"},
    
    {"url": "getusersprogressinunits", "params": "unit_id:1609,user_id:1", "method": "GET"},
    {"url": "getuserstatusincourse", "params": "course_id:1,user_id:1", "method": "GET"},
    
    
    {"url": "forgotusername", "params": "email:example@example.com", "method": "GET"},
    {"url": "userlogin", "params": "", "method": "GET"},
    {"url": "userlogout", "params": "", "method": "GET"},
    
    {"url": "gettimeline", "params": "", "method": "GET"},
    
    {"url": "getcustomregistrationfields", "params": "", "method": "GET"},
    {"url": "getusersbycustomfield", "params": "custom_field_value:test", "method": "GET"},
    """
    # def __getattribute__(self, name):
    #     if not str(name).startswith('_'):
    #         # cr = self._crud.get(name, None)
    #         # if cr is None:
    #         #     cr = CRUD(self._wcapi, name)
    #         #     self._crud[name] = cr
    #         return self._get_create_crud(name)
    #     return super().__getattribute__(name)


def initialize_actions():
    events = [
        "user_login_user",
        "user_register_user",
        "user_self_register",
        "user_delete_user",
        "user_undelete_user",
        "user_property_change",
        "user_create_payment",
        "user_upgrade_level",
        "user_unlock_badge",

        "course_create_course",
        "course_delete_course",
        "course_undelete_course",
        "course_property_change",
        "course_add_user",
        "course_remove_user",
        "course_completion",
        "course_failure",
        "course_reset_user_progress",

        "branch_create_branch",
        "branch_delete_branch",
        "branch_property_change",
        "branch_add_user",
        "branch_remove_user",
        "branch_add_course",
        "branch_remove_course",

        "group_create_group",
        "group_delete_group",
        "group_property_change",
        "group_add_user",
        "group_remove_user",
        "group_add_course",
        "group_remove_course",

        "certification_issue_certification",
        "certification_refresh_certification",
        "certification_remove_certification",
        "certification_expire_certification",

        "unitprogress_test_completion",
        "unitprogress_test_failed",
        "unitprogress_survey_completion",
        "unitprogress_assignment_answered",
        "unitprogress_assignment_graded",
        "unitprogress_ilt_graded",

        "notification_create_notification",
        "notification_delete_notification",
        "notification_update_notification",

        "automation_create_automation",
        "automation_delete_automation",
        "automation_update_automation",

        "reports_create_custom_report",
        "reports_delete_custom_report",
        "reports_update_custom_report",
    ]
    tp = TimelineAction.objects.bulk_create([TimelineAction(name=a, verbose_name=str(a).replace('_', ' ').title()) for a in events])


