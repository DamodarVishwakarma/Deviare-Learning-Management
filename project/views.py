import project
from django.db.models import F
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage

from django.db.models.functions import Cast

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
import numpy as np
import os
import io
import json
import base64
import requests
import pandas as pd

from random import randint
import datetime
from django.core import serializers

import boto3
from tools.decorators import data_response
from deviare import settings as deviare_settings
from main.models import (
    UserSettings,
    Company,
    Project,
    Course,
    CourseLicense,
    CourseLicenseUser,

    Assessment,
    AssessmentLicense,
    AssessmentLicenseUser,
    GCIndexAssessment,
    Apprenticeship,
    TMForumUserAssessment,
    ApprenticeshipLicense,
    ApprenticeshipLicenseUser, DeploymentLicense,

)
from main.serializers import (
    CompanySerializer,
    UserSettingsSerializer,
    CourseSerializer,
    GCIndexAssessmentSerializer,
    ProjectSerializer,
    CourseLicenseSerializer,
    CourseLicenseUserSerializer,
)
from project.serializers import (
    ProjectSummarySerializer,
    CourseLicenseDetailSerializer,
    AssessmentLicenseDetailSerializer,
    ApprenticeshipLicenseSerializer,
    AssessmentLicenseDashboardSerializer,
    ProjectViewSerializer,
    ApprenticeshipLicenseUserDisplaySerializer
)

from main.views import responsedata, get_impersonate_token
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
import logging
from django.db import transaction
from django.db.models import (Count, Sum, F, Case, When, Q, Value as V, TextField, IntegerField)
from main.tasks import assign_user_to_course_on_talent_lms

logger = logging.getLogger(__name__)

API_KEY = 'iCSYT65KEBXPKIGj4qtrSJyx3Y5clM'
URL_ADDRESS = 'https://deviare.talentlms.com/api/v1'


def description(desc):
    """used in reg courses to remove special characters"""

    spe_chars = ['?', 'â', '€™', '€', 'Æ']
    new_desc = ''

    for item in desc:
        if item not in spe_chars:
            new_desc += item

    return new_desc


class CreateProject(APIView):
    """Logged-in super admin can create a project"""

    def post(self, request):
        from pprint import pprint
        # Auth check
        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Check if project exists
            pprint(request.data, indent=2)
            if Project.objects.filter(
                    project_name=request.data.get("project_name")
            ).exists():
                return Response(
                    responsedata(False, "Project already exists"),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            with transaction.atomic():
                """
                Project does not exist. Create Project
                along with its dependencies, i.e CourseLicense and Assessment License.
                Return 200 response on succesful creation.
                """
                # Company, Admin, created by check
                if request.data.get("company_id") and request.data.get("company_admin_id"):
                    customer = request.data.get("company_id")
                    customer_admin = dict(uuid=request.data.get("company_admin_id"))
                    user = list(
                        UserSettings.objects.filter(userName=request.user.username).values(
                            "uuid"
                        )
                    )[0]
                else:
                    return Response(
                        responsedata(False, "Missing some details"),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Creating Project
                data = {
                    "company_id": customer,
                    "project_admin_id": request.data.get('project_admin_id'),
                    "company_admin_id": request.data.get('company_admin_id'),
                    "superadmin_id": user["uuid"],
                    "description": request.data.get('description'),
                    "project_name": request.data.get('project_name')
                }

                serializer = ProjectSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                project_data = {
                    "uuid": serializer.data.get("uuid"),
                    "company": serializer.data.get("company_id"),
                }
                project = project_data

                # Assigning Courses
                for course in request.data.get("course", []):
                    if len(course.get('course_id', '')) > 1:
                        # Check if course already exists
                        if CourseLicense.objects.filter(
                                project_id=project["uuid"], course_id=course["course_id"]
                        ).exists():
                            continue

                        # Saving Course License
                        data = {
                            "course_id": course["course_id"],
                            "count": course["count"],
                            "project_id": project["uuid"],
                        }

                        serializer = CourseLicenseSerializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                # Assigning Assessments
                for assessment in request.data.get("assessment", []):
                    if len(assessment.get('assessment_id', '')) > 1:
                        if 'uuid' in project:
                            count = assessment.get('count', 1)
                            data = {
                                "assessment_id_id": assessment["assessment_id"],
                                "project_id_id": project["uuid"],
                            }
                            data_count = {
                                "count": count if str(count).isdigit() else 1,
                            }
                            qs = AssessmentLicense.objects.filter(**data)
                            if qs.exists():
                                a = qs.first()
                                a.count = count
                                a.save()
                            else:
                                data.update(data_count)
                                ast = AssessmentLicense.objects.create(**data)
                                ast.save()
                for apprenticeship in request.data.get("apprenticeship", []):
                    if len(apprenticeship.get('apprenticeship_id', '')) > 1:
                        if 'uuid' in project:
                            count = apprenticeship.get('count', 1)
                            data = {
                                "apprenticeship_id": apprenticeship["apprenticeship_id"],
                                "project_id": project["uuid"],
                            }
                            data_count = {
                                "count": count if str(count).isdigit() else 1,
                            }
                            qs = ApprenticeshipLicense.objects.filter(**data)
                            if qs.exists():
                                a = qs.first()
                                a.count = count
                                a.save()
                            else:
                                data.update(data_count)
                                ap = ApprenticeshipLicense.objects.create(**data)
                                ap.save()
            # Everything worked well
            return Response(
                responsedata(True, "Project created successfully", project_data),
                status=status.HTTP_200_OK,
            )
        except Exception as exc:
            logger.exception(exc)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LicenseInformation(APIView):
    """To get license information for a project"""

    def post(self, request):

        if request.data.get("project_id"):
            project = request.data.get("project_id")
            courses_info = list(
                CourseLicense.objects.filter(
                    project_id=project
                ).values("course_id", "course_id__name", "count")
            )
            assessment_info = list(AssessmentLicense.objects.filter(
                project_id=project
            ).values("assessment_id", "assessment_id__name", "count"))
            apprenticeship_info = list(ApprenticeshipLicense.objects.filter(
                project_id=project
            ).values("apprenticeship_id", "apprenticeship__name", "count"))

            # New Edited
            deployment_info = list(DeploymentLicense.objects.filter(
                project_id=project
            ).values("deployment_id_id", "deployment_id__name", "count"))
            # New Edited

            data = {
                "courses": courses_info,
                'assessments': assessment_info,
                'apprenticeships': apprenticeship_info,
                'deployments': deployment_info  # Edited
            }

            return Response(
                responsedata(True, "License Info fetched", data),
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                responsedata(False, "Project ID missing"),
                status=status.HTTP_400_BAD_REQUEST,
            )


class CustomerUsers(APIView):
    """To get list of users belonging to a company"""

    @data_response
    def post(self, request, *args, **kwargs):
        values_args = ["uuid", "customer_users", 'role', 'sub_role']
        filter_kw = False
        annot_kw = {'customer_users': F("userName")}
        if request.data.get("company") and request.data.get("company") != 'null':
            filter_kw = dict(customers__in=[request.data.get("company")])
        else:
            print(kwargs)
            if request.userAuth.role in ['companyadmin', 'projectadmin', 'gcologist']:
                filter_kw = dict(customers__in=request.userAuth.customers.values_list('customers'))
            # if request.userAuth.role == 'cadmin':
            #     filter_kw = dict(customers__in=request.userAuth.customers.values_list('customers'))
        if filter_kw is not False:
            customer_users = list(UserSettings.objects.filter(
                **filter_kw
            ).annotate(**annot_kw).values(
                *values_args
            ).order_by("customer_users"))

            return Response(
                responsedata(True, "Customer users fetched", customer_users),
                status=status.HTTP_200_OK,
            )
        elif request.userAuth.role == 'superadmin':
            customer_users = list(UserSettings.objects.all(

            ).annotate(**annot_kw).values(
                *values_args
            ).order_by("customer_users").exclude(role='superadmin'))

            return Response(
                responsedata(True, "Customer users fetched", customer_users),
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                responsedata(False, "Company ID missing"),
                status=status.HTTP_400_BAD_REQUEST,
            )


def clean_uuid(uuid='', **kwargs):
    return str(uuid).replace('-', '')


def safe_int(x):
    return int(x) if x is not None and type(x) not in (pd.NaT, np.NAN, np.NaN, np.Inf, bool,) else 0


class UserAllocation(APIView):
    """To allocate user as per license"""

    def put(self, request, pk):
        try:
            Project.objects.get(uuid=pk)
        except:
            return Response(
                responsedata(False, "Invalid Project ID"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Course Allocation
        if request.data.get("courses", False):
            for course in request.data.get("courses"):
                try:

                    course_license_id = list(
                        CourseLicense.objects.filter(
                            project_id=pk, course_id=course["course_id"]
                        ).values("uuid", "count")
                    )[0]
                    data = {
                        "course_license_id": course_license_id["uuid"],
                        "user_id_id__in": [user['uuid'] for user in course["user"]],
                    }
                    CourseLicenseUser.objects.filter(**data).delete()
                except IndexError:
                    '''
                    In some cases with manipulated data in db, we are getting index error while. It wont be real case scenario.
                    '''
                    pass
        if request.data.get("assessments", False):
            for assessment in request.data.get("assessments"):
                assessment_license_id = list(
                    AssessmentLicense.objects.filter(
                        project_id=pk, assessment_id=assessment["assessment_id"]
                    ).values("uuid", "count")
                )
                if (len(assessment_license_id) > 0):
                    data = {
                        "assessment_license_id": assessment_license_id[0]["uuid"],
                        "user_id_id__in": [user['uuid'] for user in assessment["user"]],
                    }
                    AssessmentLicenseUser.objects.filter(**data).delete()
        if request.data.get("apprenticeships", False):
            for course in request.data.get("apprenticeships"):
                try:
                    course_license_id = list(
                        ApprenticeshipLicense.objects.filter(
                            project_id=pk, apprenticeship_id=course["apprenticeship_id"]
                        ).values("uuid", "count")
                    )[0]
                    data = {
                        "apprenticeship_license_id": course_license_id["uuid"],
                        "user_id__in": [user['uuid'] for user in course["user"]],
                    }
                    ApprenticeshipLicenseUser.objects.filter(**data).delete()
                except IndexError:
                    # In some cases with manipulated data in db, we are getting index error while. It wont be real case scenario.
                    pass
        return Response(
            responsedata(True, "Users Unallocated", ), status=status.HTTP_200_OK
        )

    def post(self, request, pk):
        # Checking Project ID
        try:
            Project.objects.get(uuid=pk)
        except Project.DoesNotExist:
            return Response(
                responsedata(False, "Invalid Project ID"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        ret = {

        }
        # Course Allocation
        if request.data.get("courses", False):
            ret['courses'] = {'added': [], 'to_remove': [], 'new_list': []}
            for course in request.data.get("courses"):
                try:
                    course_license_id = list(
                        CourseLicense.objects.filter(
                            project_id=pk, course_id=course["course_id"]
                        ).values("uuid", "count")
                    )[0]

                    # Saving Allocation record
                    current_users = []
                    for user in course["user"]:
                        current_users.append(user["uuid"].replace("-", ""))

                        user = list(
                            UserSettings.objects.filter(uuid=user["uuid"]).values("uuid")
                        )[0]["uuid"]
                        data = {
                            "course_license_id": course_license_id["uuid"],
                            "user_id": user,
                        }

                        # Check if already existing
                        if CourseLicenseUser.objects.filter(
                                course_license_id=course_license_id["uuid"], user_id=user
                        ).exists():
                            continue

                        serializer = CourseLicenseUserSerializer(data=data)
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()

                    # Deleting deselected users
                    all_users = []
                    all_cl_users = list(
                        CourseLicenseUser.objects.filter(
                            course_license_id=course_license_id["uuid"]
                        ).values("user_id")
                    )
                    for cl_user in all_cl_users:
                        cl_user["user_id"] = str(cl_user["user_id"]).replace("-", "")
                        all_users.append(cl_user["user_id"])
                except IndexError:
                    pass
            assign_user_to_course_on_talent_lms.apply_async(kwargs=request.data)
        if request.data.get('assessments', False):
            for assessment in request.data.get('assessments'):
                assessment_license_id = list(
                    AssessmentLicense.objects.filter(
                        project_id=pk, assessment_id=assessment["assessment_id"]
                    ).values("uuid", "count")
                )[0]

                # Saving Allocation record
                #
                allocate_assessments = []
                filter_kw = {
                    "assessment_license_id_id": assessment_license_id["uuid"],
                }
                qs = AssessmentLicenseUser.objects.filter(**filter_kw)
                existing = list(qs.values_list("user_id", flat=True))
                for user in assessment["user"]:
                    if user["uuid"] not in existing:
                        user = user["uuid"]
                        data = {
                            "user_id_id": user,
                        }
                        # Check if already existing
                        if not qs.filter(**data).exists():
                            data.update(filter_kw)
                            allocate_assessments.append(AssessmentLicenseUser(**data))
                # print(allocate_assessments)
                tmp = AssessmentLicenseUser.objects.bulk_create(allocate_assessments)
        if request.data.get('apprenticeships', False):
            for apprenticeship in request.data.get('apprenticeships'):
                apprenticeship_license_id = list(
                    ApprenticeshipLicense.objects.filter(
                        project_id=pk, apprenticeship_id=apprenticeship["apprenticeship_id"]
                    ).values("uuid", "count")
                )[0]

                # Saving Allocation record
                #
                allocate_apprenticeships = []
                filter_kw = {
                    "apprenticeship_license_id": apprenticeship_license_id["uuid"],
                }
                qs = ApprenticeshipLicenseUser.objects.filter(**filter_kw)
                existing = list(qs.values_list("user_id", flat=True))
                for user in apprenticeship["user"]:
                    if user["uuid"] not in existing:
                        user = user["uuid"]
                        data = {
                            "user_id": user,
                        }
                        # Check if already existing
                        if not qs.filter(**data).exists():
                            data.update(filter_kw)
                            allocate_apprenticeships.append(ApprenticeshipLicenseUser(**data))
                # print(allocate_apprenticeships)
                tmp = ApprenticeshipLicenseUser.objects.bulk_create(allocate_apprenticeships)
        return Response(
            responsedata(True, "Users Allocated", ), status=status.HTTP_200_OK
        )


class ProjectList(generics.ListAPIView):
    """to list project, search and pagination implementation"""

    search_fields = ["project_name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self, role, user):
        if role == "superadmin":
            return Project.objects.filter(~Q(is_delete=1)).order_by("project_name")


        elif role == "customeradmin":

            company_id = list(
                UserSettings.objects.filter(uuid=user).values_list('customers', flat=True)
            )[0]
            return Project.objects.filter(Q(company_id=company_id) | ~Q(is_delete=1)).order_by(
                "project_name"
            )
        elif role == "projectadmin":
            return Project.objects.filter(Q(project_admin=user) | ~Q(is_delete=1)).order_by(
                "project_name"
            )
        else:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    @data_response
    def get(self, request, **kw):

        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.userAuth

        # qs = self.filter_queryset(self.get_queryset(user["role"], user["uuid"]))
        instance = self.filter_queryset(self.get_queryset(user.role, user.uuid))

        columns = dict(
            user_count='total_users',
            uuid='project_uuid',
            company_id_id='company_uuid',
            company_admin_id_id='company_admin_id',
            company_admin_name='company_admin'
        )
        fields = ['startDate', 'project_name', 'total_course', 'status', 'project_admin_id', 'project_admin_name',
                  'company_name']
        fields.extend(columns.keys())

        df = ProjectSummarySerializer(instance, fields=fields, many=True).df.rename(
            index=str, columns=columns)
        # df["created_at"] = df["created_at"].dt.strftime("%d/%m/%Y")
        new_project_list = df.to_dict(orient='records')

        pagenumber = request.GET.get("page", 0)
        if pagenumber == 0:
            return JsonResponse(
                {'results': new_project_list, 'status': True},
                safe=False,
            )
        # o = (pagenumber - 1) * 10
        # new_project_list = list(ProjectListSerializer(qs, many=True).data)

        paginator = Paginator(new_project_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
                'status': True
            },
            safe=False,
        )


class LicenseList(APIView):

    def get(self, request):

        if request.auth is None:
            return Response(responsedata(False, "You are Unauthorized"), status=status.HTTP_400_BAD_REQUEST)

        user = UserSettings.objects.filter(userName=request.user.username).values().first()

        if user["role"] == "superadmin":
            project_list = list(Project.objects.all().values().order_by("project_name"))

        elif user["role"] == "customeradmin":

            company_id = list(UserSettings.objects.filter(uuid=user['uuid']).values_list('customers', flat=True))
            project_list = list(Project.objects.filter(company_id__in=company_id).values().order_by("project_name"))
        elif user["role"] == "projectadmin":

            company_id = list(
                UserSettings.objects.filter(uuid=user['uuid']).values_list('allocated_project', flat=True))
            project_list = list(Project.objects.filter(pk__in=company_id).values().order_by("project_name"))

        else:
            return Response(responsedata(False, "You are Unauthorized"), status=status.HTTP_400_BAD_REQUEST)

        new_project_list = []
        for project in project_list:
            new_project = {}

            new_project["project_uuid"] = project["uuid"]
            new_project["project_name"] = project["project_name"]

            new_project_list.append(new_project)

        return Response(responsedata(True, "Project list", new_project_list), status=status.HTTP_200_OK)


class ProjectDetail(APIView):
    """To view, update or delete a project"""

    def delete(self, request, pk):
        project = Project.objects.filter(uuid=pk)
        project.delete()
        return Response(
            responsedata(True, "Project Deleted"), status=status.HTTP_200_OK
        )

    def get(self, request, pk):

        def dl(data):
            return json.loads(json.dumps(data, default=str))

        project_qs = Project.objects.filter(uuid=pk).first()
        serializer = ProjectSummarySerializer(project_qs)
        project = serializer.data

        assessments = dl(list(Assessment.objects.values('uuid', 'name')))
        assessment_licenses = dl(list(AssessmentLicense.objects.filter(
            project_id=pk
        ).values('assessment_id', 'assessment_id__name', 'count')))

        # Apprenticeships
        apprenticeships = dl(list(Apprenticeship.objects.values('uuid', 'name')))
        apprenticeship_licenses = dl(list(ApprenticeshipLicense.objects.filter(
            project_id=pk
        ).values('apprenticeship_id', 'apprenticeship__name', 'count')))
        new_course_licenses = CourseLicenseDetailSerializer(
            project_qs.course_licenses.all(), many=True
        ).df.rename(index=str, columns={'users': 'user'}).to_dict(orient='records')

        # project = project[0]
        project["project_id"] = project.pop("uuid")
        project['assessments'] = assessments
        project['apprenticeships'] = apprenticeships
        project["assign_licenses"] = {
            "course": new_course_licenses,
            'assessment': assessment_licenses,
            'apprenticeship': apprenticeship_licenses
        }
        project["allocate_users"] = {"course": new_course_licenses}

        return Response(
            responsedata(True, "Project retrieved successfully", project),
            status=status.HTTP_200_OK,
        )

    def post(self, request, pk):
        if request.data.get("is_delete") and request.data.get("is_delete") == 1:
            from django.http import JsonResponse
            try:
                project = Project.objects.get(uuid=pk)
                project.is_delete = request.data.get("is_delete")
                project.save()
                project_data = json.loads(serializers.serialize('json', [project, ]))

                return JsonResponse({"message": "Project deleted successfully", "status": True, "data": project_data})
            except:
                return JsonResponse({"message": "Project can't deleted", "status": False})
        else:
            return JsonResponse({"message": "Project can't deleted", "status": False})

    def put(self, request, pk):

        if request.data.get("project_name"):
            # Check if project name already exists
            if Project.objects.filter(
                    project_name=request.data.get("project_name")
            ).exists():
                if Project.objects.filter(uuid=pk).values("project_name").first()[
                    "project_name"
                ] != request.data.get("project_name"):
                    return Response(
                        responsedata(False, "Project already exists"),
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Saving endDate if status is complete
            if request.data.get("status") == "Complete":
                today = datetime.date.today()
                request.data["endDate"] = today
            if request.data.get("status") == "open":
                request.data["endDate"] = None

            # Checking Customer and Customer Admin
            # if we got none in then it should be considered as null
            if request.data.get('project_admin') == "None":
                request.data['project_admin'] = None

            if request.data.get('company_admin_id') == "None":
                request.data['company_admin_id'] = None

            try:
                UserSettings.objects.get(
                    uuid=request.data.get("company_admin_id"),
                    customers=request.data["company_id"],
                )
            except:
                pass
                # return Response(
                #     responsedata(False, "Company Admin Error"),
                #     status=status.HTTP_400_BAD_REQUEST,
                # )
            project_data = request.data.copy()
            course_data = project_data.pop('course') if 'course' in project_data else None
            assessment_data = project_data.pop('assessment') if 'assessment' in project_data else None
            appren_data = project_data.pop('apprenticeship') if 'apprenticeship' in project_data else None
            # Updating Project
            project = Project.objects.filter(uuid=pk).first()
            serializer = ProjectSerializer(project, data=project_data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

            # Updating Courses
            if course_data is not None and type(course_data) in (list, tuple):
                if len(course_data[0]['course_id']) > 1:
                    course_ids = []
                    for each_course in course_data:
                        each_course['project_id'] = project.uuid
                        # Updating existing courses in Project
                        l = ['course_id', 'project_id']
                        cl_id_kwargs = {f"{k}_id": v for k, v in each_course.items() if k in l}
                        crs, c = CourseLicense.objects.get_or_create(**cl_id_kwargs)
                        count = each_course.get('count', 1)
                        crs.count = count if str(count).isdigit() else 1
                        crs.save()

            # Create Project assessments
            if assessment_data is not None and type(assessment_data) in (list, tuple):
                if len(assessment_data[0]['assessment_id']) > 1:
                    for assessment in assessment_data:
                        if 'assessment_id' in assessment and project:
                            count = assessment.get('count', 1)
                            data = {
                                "assessment_id_id": assessment["assessment_id"],
                                "project_id_id": project.uuid,
                            }

                            data_count = {
                                "count": count if str(count).isdigit() else 1,
                            }
                            qs = AssessmentLicense.objects.filter(**data)
                            if qs.exists():
                                a = qs.first()
                                a.count = count
                                a.save()
                            else:
                                data.update(data_count)
                                ap = AssessmentLicense.objects.create(**data)
                                ap.save()
            # Create Project Apprenticeships
            if appren_data is not None and type(appren_data) in (list, tuple):
                if len(appren_data[0]['apprenticeship_id']) > 1:
                    for apprenticeship in appren_data:
                        if 'apprenticeship_id' in apprenticeship and project:
                            count = apprenticeship.get('count', 1)
                            data = {
                                "apprenticeship_id": apprenticeship["apprenticeship_id"],
                                "project_id": project.uuid,
                            }
                            data_count = {
                                "count": count if str(count).isdigit() else 1,
                            }
                            qs = ApprenticeshipLicense.objects.filter(**data)
                            if qs.exists():
                                a = qs.first()
                                a.count = count
                                a.save()
                            else:
                                data.update(data_count)
                                ap = ApprenticeshipLicense.objects.create(**data)
                                ap.save()

            return Response(
                responsedata(True, "Project updated successfully", project_data),
                status=status.HTTP_200_OK,
            )


class LicenseDetail(APIView):
    """to get license detail in update license for user view"""

    @data_response
    def put(self, request, pk, *args, **kwargs):
        assessment_delete = request.data.get('assessments', [])
        ret = {}
        c = request.data.get('courses', [])
        # Course
        try:
            if len(c) > 0:
                ret['courses'] = CourseLicense.objects.filter(
                    project_id=pk,
                    course_id__in=[a.get("course_id") for a in c]
                ).delete()

        except Exception as exc:
            logger.exception(exc)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Assessment
        try:
            if len(assessment_delete) > 0:
                ret['assessments'] = AssessmentLicense.objects.filter(
                    project_id=pk,
                    assessment_id__in=[a.get("assessment_id") for a in assessment_delete]
                ).delete()

        except Exception as exc:
            logger.exception(exc)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Apperanticeships
        try:
            apprenticeships_delete = request.data.get('apprenticeships', [])
            if len(apprenticeships_delete) > 0:
                ret['apprenticeships'] = ApprenticeshipLicense.objects.filter(
                    project_id=pk,
                    apprenticeship_id__in=[a.get("apprenticeship_id") for a in apprenticeships_delete]).delete()

        except Exception as exc:
            logger.exception(exc)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Deployments
        try:
            deployments_delete = request.data.get('deployments', [])
            if len(apprenticeships_delete) > 0:
                ret['deployments'] = DeploymentLicense.objects.filter(
                    project_id=pk,
                    deployment_id_id__in=[a.get("deployment_id") for a in deployments_delete]).delete()

        except Exception as exc:
            logger.exception(exc)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return {'data': ret}

    @data_response
    def get(self, request, pk, *args, **kwargs):
        try:
            proj = get_object_or_404(Project, pk=pk)
            ser = ProjectViewSerializer(get_object_or_404(Project, pk=pk),
                                        fields=[
                                            'users',
                                        ])
            #  {k.replace('_license', ''): v for k, v in ser.data.items()})
            skwargs = dict(many=True, fields=['uuid', 'cl_uuid', 'users', 'count', 'user_count',
                                              'course_id', 'course_name',
                                              'assessment_id', ' assessment_name',
                                              'apprenticeship_id', 'apprenticeship_name',
                                              ])
            if 'simple' in kwargs:
                skwargs['fields'] = ['uuid', 'users', 'count', 'product_id', 'product_name', 'product_type']

            # if 'all' in kwargs:
            #     skwargs.pop('fields')
            result = {
                'courses': CourseLicenseDetailSerializer(proj.course_licenses.all(), **skwargs).data,
                'assessments': AssessmentLicenseDetailSerializer(proj.assessment_licenses.all(), **skwargs).data,
                'apprenticeships': ApprenticeshipLicenseSerializer(proj.apprenticeship_licenses.all(), **skwargs).data
            }
            result.update(ser.data)
            return Response(
                responsedata(True, "Project retrieved successfully",
                             result),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                responsedata(False, "Project not found"),
                status=status.HTTP_404_NOT_FOUND
            )


class CourseCatalog(APIView):
    """To get course catalog for user view"""

    def get(self, request):

        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = request.user

        try:
            token = base64.b64encode(
                (str(get_impersonate_token(user.username))).encode("utf-8")
            )
        except:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = UserSettings.objects.filter(userName=user.username).values().first()
        courses = Course.objects.all().values()

        # Creating list of categories
        category_list = []
        for course in courses:
            category_list.append(course["category"])
        category_list = list(set(category_list))

        # User Courses
        course_licenses_ids = CourseLicenseUser.objects.filter(
            user_id=user["uuid"]
        ).values("course_license_id")
        user_courses = []
        for course_licenses_id in course_licenses_ids:
            course_id = (
                CourseLicense.objects.filter(
                    uuid=course_licenses_id["course_license_id"]
                )
                    .values("course_id")
                    .first()["course_id"]
            )
            user_courses.append(course_id)

        # Arranging courses, category-wise
        catalog = []
        for category in category_list:

            courses_list = []
            for course in courses:

                # Unlocking user's assigned courses
                course["locked"] = False if course["uuid"] in user_courses else True
                if course["uuid"] in user_courses:
                    course["token"] = token

                if category == course["category"]:
                    courses_list.append(course)

            catalog.append({"category": category, "courses": courses_list})

        # Moving Master Programs on top
        for item in catalog:
            if item["category"] == "Master Programs":
                catalog.insert(0, catalog.pop(catalog.index(item)))

        return Response(
            responsedata(True, "Course Catalog retrieved successfully", catalog),
            status=status.HTTP_200_OK,
        )


class RegisteredCourses(APIView):
    """To get details of all the registered courses of users"""

    def get(self, request):

        if request.auth is None:
            return Response(responsedata(False, "You are Unauthorized"), status=status.HTTP_400_BAD_REQUEST)

        try:
            token = base64.b64encode((str(get_impersonate_token(request.user.username))).encode("utf-8"))
        except:
            return Response(responsedata(False, "You are Unauthorized"), status=status.HTTP_400_BAD_REQUEST)

        user = UserSettings.objects.filter(userName=request.user.username).values().first()

        course_licenses_ids = CourseLicenseUser.objects.filter(
            user_id=user["uuid"]
        ).values("pk", "course_license_id", "course_completion")

        courses = []
        category_list = []
        for course_licenses_id in course_licenses_ids:
            try:
                course_id = (
                    CourseLicense.objects.filter(uuid=course_licenses_id["course_license_id"]).values(
                        "course_id").first()[
                        "course_id"])
                course_name = Course.objects.filter(uuid=course_id).values().first()
                course_completion = course_licenses_id["course_completion"]
                try:
                    if course_name['course_id_talent_lms'] != None:
                        # Update course completion progress for
                        # courses provided by TalentLMS

                        try:
                            user_id = user['user_id_talentlms']
                            course_id_lms = course_name['course_id_talent_lms']

                            url = "%s/getuserstatusincourse/course_id:%s,user_id:%s" % (
                                URL_ADDRESS, course_id_lms, user_id)

                            response = requests.request(
                                "GET", url, auth=(API_KEY, ''), headers={}, data={})

                            if response.status_code == 200:
                                content = json.loads(response.text)
                                course_completion = content['completion_percentage']
                                cl = CourseLicenseUser.objects.get(pk=course_licenses_id['pk'])
                                cl.course_completion = course_completion
                                cl.save()

                            else:
                                logger.critical(response.text)
                        except Exception as exc:
                            logger.exception(exc)
                            pass
                except Exception as exc:
                    logger.exception(exc)
                    pass

                courses.append(
                    {
                        "course_id": course_id,
                        "course_name": course_name["name"],
                        "course_completion": course_completion,
                        # "description": course_name["description"],
                        # "course_completion": course_licenses_id["course_completion"],
                        "description": description(course_name["description"]),
                        "provider": course_name["provider"],
                        "link": course_name["link"],
                        "category": course_name["category"],
                        "token": token,
                        "course_id_talent_lms": course_name['course_id_talent_lms']
                    })
                if course_name["category"] not in category_list:
                    category_list.append(course_name["category"])
            except Exception as exc:
                logger.exception(exc)
                pass

        # Arrnaging respone category wise
        all_category_wise = []
        for category in category_list:
            category_wise = []
            for item in courses:
                if category == item["category"]:
                    category_wise.append(item)

            all_category_wise.append({"category": category, "data": category_wise})

        return Response(responsedata(True, "Courses retrieved successfully", all_category_wise),
                        status=status.HTTP_200_OK)


# Reports


class CustomersReport(generics.ListAPIView):
    """To get list of customers, customer admins, projects and users"""

    search_fields = ["name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self):
        return Company.objects.all().order_by("name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        instance = self.filter_queryset(self.get_queryset())

        annot_kwargs = dict(
            projects_count=Count('projects__uuid', distinct=True),
            # admins_count=Sum(Case(
            #     When(Q(company__role="customeradmin"), V(1)), default=V(0),
            #     output_field=IntegerField())),
            # users_count=Sum(Case(
            #     When(Q(company__role="user"), V(1)), default=V(0),
            #     output_field=IntegerField())),
            assessment_available=Count('tmforum_assessment__assessment__responses'),
        )
        customer_list = list(instance.annotate(**annot_kwargs).values())

        for customer in customer_list:

            # Start Date
            customer["created_at"] = customer["created_at"].strftime("%d/%m/%Y")

            # Admins
            customer["admins_count"] = UserSettings.objects.filter(customers=customer["uuid"],
                                                                   role="customeradmin").count()
            if customer["admins_count"] == 1:
                customer["admin_name"] = (
                    UserSettings.objects.filter(customers=customer["uuid"], role="customeradmin").values(
                        "userName").first()["userName"])

            # Users
            customer["users_count"] = UserSettings.objects.filter(
                customers=customer["uuid"], role="user"
            ).count()

        pagenumber = request.GET.get("page", 1)
        paginator = Paginator(customer_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class AdminsReport(generics.ListAPIView):
    """To get list of customer admins"""

    search_fields = ["firstName", "lastName", "email"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self, company_id):
        return UserSettings.objects.filter(
            role="customeradmin", customers=company_id
        ).order_by("firstName")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        if not request.GET.get("uuid"):
            return Response(responsedata(False, "Customer not provided"), status=status.HTTP_400_BAD_REQUEST)

        instance = self.filter_queryset(self.get_queryset(request.GET.get("uuid")))
        admins_list = list(instance.annotate(
            assessment_available=Count('companyID__tmforum_assessment_responses__uuid')
        ).values())

        for admin in admins_list:

            # Removing unwanted data
            keys_to_remove = [
                "created_at",
                "updated_at",
                "user_id",
                "reset_id",
                "validated",
                "userName",
                "password",
                "location",
                "contact_no",
                "companyID_id",
                "country",
                "role",
            ]
            for key in keys_to_remove:
                del admin[key]

        pagenumber = request.GET.get("page", 1)
        paginator = Paginator(admins_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class ProjectsReport(generics.ListAPIView):
    """To get details of projects as per customer"""

    search_fields = ["project_name"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self, **kwargs):
        return Project.objects.filter(**kwargs).order_by("project_name")

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        ident = {'company_id' if k == 'uuid' else k: request.GET.get(k) for k in ['uuid', 'project_id', 'company_id'] if
                 request.GET.get(k, None)}
        if len(ident) == 0:
            return Response(
                responsedata(False, "Customer not provided"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        if 'project_id' in ident:
            ident['pk'] = ident.pop('project_id')
        instance = self.filter_queryset(self.get_queryset(**ident))
        df = ProjectSummarySerializer(instance, many=True).df.rename(index=str, columns=dict(
            company_admin_id_id='company_admin_id'
        ))
        data_list = []
        if not df.empty:
            if 'created_at' in df.columns.tolist():
                df["created_at"] = df["created_at"].apply(
                    lambda x: x.strftime("%d/%m/%Y") if type(x) in (datetime.datetime, datetime.date) else str(x))
            data_list = df.to_dict(orient='records')

        # Pagination
        pagenumber = request.GET.get("page", 0)
        if pagenumber == 0:
            return JsonResponse(
                {'results': data_list, 'status': True},
                safe=False,
            )
        paginator = Paginator(data_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                'status': True,
                "results": data_to_show,
            },
            safe=False,
        )


class UsersReport(generics.ListAPIView):
    """To get details of users as per customer's project"""

    search_fields = ["user_id__firstName", "user_id__lastName", "user_id__email"]
    filter_backends = (filters.SearchFilter,)

    def get_queryset(self, project_id):
        clu_ids = []
        user_ids = []
        course_licenses = CourseLicense.objects.filter(project_id=project_id).values()
        for course_license in course_licenses:
            cl_users = CourseLicenseUser.objects.filter(
                course_license_id=course_license["uuid"]
            ).values()
            for user in cl_users:
                if user["user_id_id"] not in user_ids:
                    clu_ids.append(user["uuid"])
                    user_ids.append(user["user_id_id"])

        return CourseLicenseUser.objects.filter(uuid__in=clu_ids).order_by(
            "user_id__firstName"
        )

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):

        if not request.GET.get("uuid"):
            return Response(
                responsedata(False, "Project not provided"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        value_args = [
            'user_id__uuid',
            'user_id__firstName',
            'user_id__lastName',
            'user_id__email',
            'user_id__profile_image',
            'course_license_id__project_id__project_name',
            'course_license_id__course_id__name',
            'course_completion'
        ]

        def clean_key(x):
            for k in [
                'user_id__',
                'course_license_id__project_id__',
                'license_id__course_id__'
            ]:
                x = x.replace(k, '')
            return x.lower()

        rename_cols = {k: clean_key(k) for k in value_args}
        instance = self.filter_queryset(self.get_queryset(request.GET.get("uuid")))
        user_list = pd.DataFrame(instance.values(*value_args)).rename(
            index=str,
            columns=rename_cols
        )  # .groupby('uuid', as_index=False).agg({'course_name': 'unique'})
        user_list = user_list.fillna(value=0).to_dict(orient='records')
        # Pagination
        pagenumber = request.GET.get("page", 0)
        if pagenumber == 0:
            return JsonResponse(
                {'results': user_list, 'status': True},
                safe=False,
            )
        paginator = Paginator(user_list, 10)

        if int(pagenumber) > paginator.num_pages:
            raise ValidationError("Not enough pages", code=404)
        try:
            previous_page_number = paginator.page(pagenumber).previous_page_number()
        except EmptyPage:
            previous_page_number = None
        try:
            next_page_number = paginator.page(pagenumber).next_page_number()
        except EmptyPage:
            next_page_number = None
        data_to_show = paginator.page(pagenumber).object_list

        return JsonResponse(
            {
                "pagination": {
                    "previous_page": previous_page_number,
                    "is_previous_page": paginator.page(pagenumber).has_previous(),
                    "next_page": next_page_number,
                    "is_next_page": paginator.page(pagenumber).has_next(),
                    "start_index": paginator.page(pagenumber).start_index(),
                    "end_index": paginator.page(pagenumber).end_index(),
                    "total_entries": paginator.count,
                    "total_pages": paginator.num_pages,
                    "page": int(pagenumber),
                },
                "results": data_to_show,
            },
            safe=False,
        )


class UserDetailReport(APIView):
    """To get simplilearn's data"""

    def post(self, request):

        if not request.data.get("user_id") and not request.data.get("project_id"):
            return Response(responsedata(False, "User or project details not provided"),
                            status=status.HTTP_400_BAD_REQUEST)
        from django.db.models.functions import Concat
        user_id = request.data.get("user_id")
        project_id = request.data.get("user_id")
        user = UserSettings.objects.filter(
            uuid=request.data.get("user_id")
        ).annotate(
            username=F('userName'),
            fullname=Concat(F('firstName'), F('lastName')),
            member_since=F('created_at')
        ).values(
            *list('uuid,username,fullname,member_since,email,profile_image'.split(','))
        ).first()
        customers = Project.objects.filter(uuid=request.data.get("project_id")).annotate(
            company_uuid=F('company_id'),
            company_name=F('company_id__name'),
            company_country=F('company_id__country'),
        ).values(
            'company_uuid', 'company_name', 'company_country'
        ).first()

        # User Data
        data = user.copy()
        data.update(customers)
        data["member_since"] = data["member_since"].strftime("%d/%m/%Y")
        data["skills_transformation"] = []
        # User Courses Data
        annot_kw = dict(
            course_uuid=F("course_license_id__course_id"),
            course_name=F("course_license_id__course_id__name"),
            course_provider=F("course_license_id__course_id__provider"),
            course_category=F("course_license_id__course_id__category"),
            courseID=F("course_license_id__course_id__course_id"),
            course_type=F("course_license_id__course_id__course_type"),
        )
        value_args = ["course_license_id", "course_completion"]
        value_args.extend(annot_kw.keys())
        course_licenses = pd.DataFrame(CourseLicenseUser.objects.filter(
            user_id=user_id,
            course_license_id__project_id=project_id,
        ).annotate(
            **annot_kw
        ).values(*value_args))
        if not course_licenses.empty:
            course_licenses = course_licenses.fillna(value=0).sort_values('course_category')

            # Category list
            category_data = {k: [] for k in course_licenses.course_category.unique().tolist()}

            def g(group):
                return {
                    'average': group['score'].mean(),
                    'category': group['course_category'].tolist()[0],
                    'data': group.to_dict(orient='records')
                }

            all_category_wise = course_licenses.groupby('course_category', as_index=False).apply(g)
            #
            # # Arrnaging respone category wise
            # all_category_wise = []
            # for category in category_list:
            #     category_wise = []
            #     score = []
            #     for item in course_licenses:
            #         if category == item["course_category"]:
            #             if "course_completion" in item:
            #                 if item["course_completion"] is None:
            #                     item["course_completion"] = 0
            #                 score.append(item["course_completion"])
            #             else:
            #                 item["course_completion"] = 0
            #                 score.append(item["course_completion"])
            #             category_wise.append(item)
            #
            #     if len(score) != 0:
            #         score = sum(score) / len(score)
            #     else:
            #         score = 0
            #
            #     all_category_wise.append(
            #         {
            #             "category": category,
            #             "average": round(score, 2),
            #             "data": category_wise,
            #         }
            #     )

            data["skills_transformation"] = all_category_wise.to_dict(orient='records')

        return Response(
            responsedata(True, "Report retrieved successfully", data),
            status=status.HTTP_200_OK,
        )


class UserViewProjects(APIView):
    """To get projects allocated to a user"""

    def get(self, request, pk):

        cl_ids = CourseLicenseUser.objects.filter(user_id=pk).values(
            "course_license_id"
        )
        projects = []

        for cl_id in cl_ids:
            cl = (
                CourseLicense.objects.filter(uuid=cl_id["course_license_id"])
                    .values("project_id", "project_id__project_name")
                    .first()
            )
            item = {
                "project_uuid": cl["project_id"],
                "project_name": cl["project_id__project_name"],
            }
            if item in projects:
                continue
            projects.append(item)

        return Response(
            responsedata(True, "Projects retrieved successfully", projects),
            status=status.HTTP_200_OK,
        )


# Download Reports
class DownloadReport(APIView):

    def get(self, request, pk):
        from datetime import datetime

        if not Company.objects.filter(uuid=pk).exists():
            return Response(responsedata(False, "Customer does not exist"), status=status.HTTP_400_BAD_REQUEST)

        if request.query_params.get('project_id'):
            if not Project.objects.filter(uuid=request.query_params.get('project_id')).exists():
                return Response(responsedata(False, "Project does not exist"), status=status.HTTP_400_BAD_REQUEST)
            data = CourseLicenseUser.objects.filter(
                course_license_id__project_id=request.query_params.get('project_id'),
                course_license_id__project_id__company_id=pk)

        else:
            data = CourseLicenseUser.objects.filter(course_license_id__project_id__company_id=pk)

        data = data.annotate(Customer=Cast("course_license_id__project_id__company_id__name", output_field=TextField()),
                             Project=Cast("course_license_id__project_id__project_name", output_field=TextField()),
                             Admin=Cast("course_license_id__project_id__company_admin_id__userName",
                                        output_field=TextField()),
                             Description=Cast("course_license_id__project_id__description", output_field=TextField()),
                             Status=Cast("course_license_id__project_id__status", output_field=TextField()),
                             StartDate=Cast("course_license_id__project_id__startDate", output_field=TextField()),
                             EndDate=Cast("course_license_id__project_id__endDate", output_field=TextField()),
                             Name=Cast("user_id__userName", output_field=TextField()),
                             Email=Cast("user_id__email", output_field=TextField()),
                             CourseName=Cast("course_license_id__course_id__name", output_field=TextField()),
                             Category=Cast("course_license_id__course_id__category", output_field=TextField()),
                             Provider=Cast("course_license_id__course_id__provider", output_field=TextField()),
                             CourseID=Cast("course_license_id__course_id__course_id", output_field=TextField()),
                             CourseType=Cast("course_license_id__course_id__course_type", output_field=TextField()),
                             Completion=Cast("course_completion", output_field=TextField())).order_by('Project', 'Name',
                                                                                                      'CourseName')

        data = list(data.values('Customer', 'Project', 'Admin', 'Description', 'Status', 'StartDate', 'EndDate', 'Name',
                                'Email', 'CourseName',
                                'Category', 'Provider', 'CourseID', 'CourseType', 'Completion'))

        data = pd.DataFrame(data)
        if data.empty:
            return Response(responsedata(False, "No Data in Query Set", ),
                            status=status.HTTP_404_NOT_FOUND)
        data['CourseID'] = data['CourseID'].apply(safe_int).astype(int)

        more_data = pd.read_csv('https://elearn-stat.s3.amazonaws.com/tmp/useractivity.csv')
        more_data = more_data.dropna(axis=1, how='all')

        more_data = more_data.rename(columns={"Learner Email": "Email", "Course Id": "CourseID"})

        df = pd.merge(data, more_data, how='left')
        df = df.drop(['Learner Name', 'Self-Learning Completion %'], axis=1)

        df = df.dropna(axis=1, how='all')

        filename = f'report_{datetime.now().strftime("%d-%m-%Y")}_{str(randint(1000, 9999))}.csv'
        data = df.to_csv(filename, index=False, header=True)

        with open(filename, "rb") as f:
            data = f.read()
        data = base64.b64encode(data)

        os.remove(filename)

        return Response(responsedata(True, "Report downloaded successfully", data), status=status.HTTP_200_OK)


def getUserDetailsCSV(filter_kwargs):
    from datetime import datetime
    from collections import OrderedDict

    rename = OrderedDict([
        ("user_id__userName", 'Name'),
        ("user_id__email", "Email"),
        ("course_license_id__course_id__name", "CourseName"),
        ("course_completion", "Completion"),
        ("course_license_id__course_id__category", "Category"),
        ("course_license_id__course_id__provider", "Provider"),
        ("course_license_id__course_id__course_id", "CourseID"),
        ("course_license_id__course_id__course_type", "CourseType"),
        ("course_license_id__project_id__company_id__name", "Customer"),
        ("course_license_id__project_id__project_name", "Project"),
        ("course_license_id__project_id__company_admin_id__userName", "Admin"),
        ("course_license_id__project_id__description", "Description"),
        ("course_license_id__project_id__status", "Status"),
        ("course_license_id__project_id__startDate", "StartDate"),
        ("course_license_id__project_id__endDate", "EndDate"), ]
    )

    qs = CourseLicenseUser.objects.filter(**filter_kwargs).values(*rename.keys()).order_by(
        'course_license_id__project_id__project_name',
        'course_license_id__course_id__category',
        'course_license_id__course_id__name'
    )

    try:

        data = pd.DataFrame(list(qs))
        if data.empty:
            return Response(responsedata(False, "No Data in Query Set", ),
                            status=status.HTTP_404_NOT_FOUND)
        data = data.rename(index=str, columns=rename)
        data['CourseID'] = data['CourseID'].apply(safe_int).astype(int)

        more_data = pd.read_csv('https://elearn-stat.s3.amazonaws.com/tmp/useractivity.csv')
        more_data = more_data.dropna(axis=1, how='all')

        more_data = more_data.rename(columns={"Learner Email": "Email", "Course Id": "CourseID"})

        df = pd.merge(data, more_data, how='left')
        df = df.drop(['Learner Name', 'Self-Learning Completion %'], axis=1)

        df = df.dropna(axis=1, how='all')

        filename = f'report_{datetime.now().strftime("%d-%m-%Y")}_{str(randint(1000, 9999))}.csv'

        r = df.to_csv(filename, index=False, header=True)

        with open(filename, "rb") as f:
            output_data = f.read()
        output_data = base64.b64encode(output_data)

        os.remove(filename)

        return Response(responsedata(True, "Report downloaded successfully", output_data),
                        status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        traceback.print_stack()
        print('~'.join(['#'] * 50))
        traceback.print_exc()
        return Response(responsedata(False, "Error Downloading"),
                        status=status.HTTP_400_BAD_REQUEST)


class UserDetailedCSV(APIView):

    def get(self, request, pk):
        if not UserSettings.objects.filter(uuid=pk).exists():
            return Response(responsedata(False, "User does not exist"), status=status.HTTP_400_BAD_REQUEST)

        return getUserDetailsCSV(dict(user_id=pk))


class ProjectUserDetailedCSV(APIView):
    @data_response
    def get(self, request, *args, **kwargs):
        project_id = kwargs.get('project_id')
        if type(project_id) not in (tuple, list):
            project_id = [project_id]
        return getUserDetailsCSV(dict(course_license_id__project_id__in=project_id))


class RegisteredAssessments(APIView):
    """To get details of all the registered assessments of users"""

    @data_response
    def patch(self, request, pk, *args, **kwargs):
        # from main.models import GCState
        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj = GCIndexAssessment.objects.get(pk=pk)
        if obj.state_id == 9:
            return dict(
                status=True,
                data={'url': obj.url},
                message='GCIndex Loaded'
            )
        if obj.state_id < 6:
            obj.state_id = 10
            obj.save()
        return dict(
            status=True,
            data={'url': obj.url},
            message='GCIndex Loaded'
        )

    @data_response
    def put(self, request, pk, *args, **kwargs):
        # from main.models import GCState
        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        obj = GCIndexAssessment.objects.get(pk=pk)
        if obj.state_id == 9:
            return dict(
                status=True,
                data={'url': obj.url},
                message='GCIndex Loaded'
            )
        if obj.state_id < 6:
            obj.state_id = 10
            obj.save()

        return dict(
            status=True,
            data={'url': obj.url},
            message='GCIndex Loaded'
        )

    @data_response
    def get(self, request, *args, **kwargs):
        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.userAuth

        qs = GCIndexAssessment.objects.filter(user=user)
        gc = dict(exists=qs.exists(), url='')
        tmqs = TMForumUserAssessment.objects.filter(owner=user)
        tm = dict(exists=tmqs.exists(), url='/tmforum/1')
        if qs.exists():
            gc.update(GCIndexAssessmentSerializer(qs.first()).data)
            gc['state'] = qs.first().state_id
        return dict(
            status=True,
            data={'gc': gc, 'tm': tm},
            message='Assessments Loaded'
        )
        # return Response(
        #     responsedata(False, "You haven't been allocated any assessments"),
        #     status=status.HTTP_404_NOT_FOUND,
        # )


class RegisteredApprenticeships(APIView):
    """To get details of all the registered Apprenticeships of users"""

    @data_response
    def get(self, request, *args, **kwargs):
        if request.auth is None:
            return Response(
                responsedata(False, "You are Unauthorized"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.userAuth

        qs = ApprenticeshipLicenseUser.objects.filter(user=user)
        ser = ApprenticeshipLicenseUserDisplaySerializer(qs, many=True)
        return dict(
            status=True,
            data=ser.data,
            message='Apprenticeships Loaded'
        )
# ssh -i pram2.pem ubuntu@34.222.118.114
# python manage.py crontab add / show / remove
