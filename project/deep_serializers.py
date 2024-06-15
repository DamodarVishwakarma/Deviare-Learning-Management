from rest_framework import serializers
from collections import OrderedDict
from tools.rest_extras import (
    DynamicFieldsModelSerializer,
    DataFrameListSerializer
)
from django.db.models import Count, Sum
from main.models import (
    Company,
    UserSettings,
    Course,
    Project,
    CourseLicense,
    CourseLicenseUser,
    ApprenticeshipLicense,
    ApprenticeshipLicenseUser,
    Experiment,
    Deployment,
    AssessmentLicense,
    AssessmentLicenseUser
)


class LicenseUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = UserSettings
        fields = ['uuid', 'userName', 'role', 'sub_role']


class CourseLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = CourseLicenseUser
        fields = ['user_id', 'uuid', 'license_id']

    # uuid = serializers.SerializerMethodField(read_only=True)
    # customer_users = serializers.SerializerMethodField(read_only=True)
    license_id = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj.user_id:
            return obj.user_id.uuid

    def get_customer_users(self, obj):
        if obj.user_id:
            return obj.user_id.userName

    def get_license_id(self, obj):
        if obj.course_license_id:
            return obj.course_license_id.uuid


class AssessmentLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicenseUser
        fields = ['user_id', 'uuid', 'license_id']

    # uuid = serializers.SerializerMethodField(read_only=True)
    # customer_users = serializers.SerializerMethodField(read_only=True)
    license_id = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj.user_id:
            return obj.user_id.uuid

    def get_customer_users(self, obj):
        if obj.user_id:
            return obj.user_id.userName

    def get_license_id(self, obj):
        if obj.assessment_license_id:
            return obj.assessment_license_id.uuid


class ApprenticeshipLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = ApprenticeshipLicenseUser
        fields = ['user_id', 'uuid', 'license_id']

    # uuid = serializers.SerializerMethodField(read_only=True)
    # userName = serializers.SerializerMethodField(read_only=True)
    license_id = serializers.SerializerMethodField(read_only=True)

    def get_user_id(self, obj):
        if obj.user:
            return obj.user.uuid

    def get_userName(self, obj):
        if obj.user:
            return obj.user.userName

    def get_license_id(self, obj):
        if obj.apprenticeship_license:
            return obj.apprenticeship_license.uuid


class CourseLicenseDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = CourseLicense
        fields = "__all__"

    users = CourseLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])
    allocated = serializers.SerializerMethodField(read_only=True)
    user_count = serializers.SerializerMethodField(read_only=True)
    completed_count = serializers.SerializerMethodField(read_only=True)
    course_name = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_allocated(self, obj):
        if obj.users:
            return obj.users.all().values_list('uuid', flat=True)

    def get_user(self, obj):
        if obj.users:
            return CourseLicenseUserDetailSerializer(obj.users.all(), many=True).data

    def get_user_count(self, obj):
        if obj.users:
            return obj.users.count()

    def get_completed_count(self, obj):
        if obj.users:
            return obj.users.filter(course_completion__gte=99.99).count()

    def get_cl_uuid(self, obj):
        if obj:
            return obj.uuid

    def get_course_name(self, obj):
        if obj.course_id:
            return obj.course_id.name


class ApprenticeshipLicenseSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = ApprenticeshipLicense
        fields = "__all__"

    users = ApprenticeshipLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])
    allocated = serializers.SerializerMethodField(read_only=True)
    user_count = serializers.SerializerMethodField(read_only=True)
    completed_count = serializers.SerializerMethodField(read_only=True)
    apprenticeship_name = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_allocated(self, obj):
        if obj.users:
            return obj.users.all().values_list('uuid', flat=True)

    def get_user_count(self, obj):
        if obj.users:
            return obj.users.count()

    def get_cl_uuid(self, obj):
        if obj:
            return obj.uuid

    def get_apprenticeship_name(self, obj):
        if obj.apprenticeship:
            return obj.apprenticeship.name


class AssessmentLicenseDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicense
        fields = "__all__"

    users = AssessmentLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])

    user_count = serializers.SerializerMethodField(read_only=True)

    assessment_name = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_user_count(self, obj):
        if obj.users:
            return obj.users.count()

    def get_cl_uuid(self, obj):
        if obj:
            return obj.uuid

    def get_assessment_name(self, obj):
        if obj.assessment_id:
            return obj.assessment_id.name


class AssessmentLicenseDashboardSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicense
        fields = "__all__"

    consumed_licenses = serializers.SerializerMethodField(read_only=True)

    def get_consumed_licenses(self, obj):
        if obj.users:
            return obj.users.count()


class ApprenticeshipLicenseDashboardSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicense
        fields = "__all__"

    consumed_licenses = serializers.SerializerMethodField(read_only=True)

    def get_consumed_licenses(self, obj):
        if obj.users:
            return obj.users.count()


class ProjectSummarySerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = Project
        fields = "__all__"

    company_name = serializers.SerializerMethodField(read_only=True)
    project_admin_name = serializers.SerializerMethodField(read_only=True)
    company_admin = serializers.SerializerMethodField(read_only=True)
    superadmin_name = serializers.SerializerMethodField(read_only=True)

    def get_company_name(self, obj):
        if obj.company_id:
            return obj.company_id.name
        return obj.company_id

    def get_superadmin_name(self, obj):
        if obj.superadmin_id:
            return obj.superadmin_id.userName
        return ''

    def get_project_admin_name(self, obj):
        if obj.project_admin:
            return obj.project_admin.userName
        return ''

    def get_company_admin(self, obj):
        if obj.company_admin_id:
            return obj.company_admin_id.userName
        return ''

    def create(self, validated_data):
        try:
            if 'course_licenses' in validated_data:
                course_licenses = validated_data.pop('course_licenses')
            if 'assessment_licenses' in validated_data:
                assessment_licenses = validated_data.pop('assessment_licenses')
            project = Project.objects.create(**validated_data)
            for data in course_licenses:
                CourseLicense.objects.create(project_id=project, **data)
            for data in assessment_licenses:
                AssessmentLicense.objects.create(project_id=project, **data)
            return project
        except Exception as e:
            return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'course_licenses' in validated_data:
            course_licenses = validated_data.pop('course_licenses')
        if 'assessment_licenses' in validated_data:
            assessment_licenses = validated_data.pop('assessment_licenses')
        for data in course_licenses:
            CourseLicense.objects.get_or_create(project_id=instance, **data)
        for data in assessment_licenses:
            AssessmentLicense.objects.get_or_create(project_id=instance, **data)
        return super().update(instance, validated_data)


class ProjectViewSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = Project
        fields = "__all__"

    company_name = serializers.SerializerMethodField(read_only=True)
    project_admin_name = serializers.SerializerMethodField(read_only=True)
    company_admin = serializers.SerializerMethodField(read_only=True)
    superadmin_name = serializers.SerializerMethodField(read_only=True)
    users = serializers.SerializerMethodField(read_only=True)

    course_licenses = CourseLicenseDetailSerializer(many=True, fields=[
        'uuid', 'count', 'course_id', 'users'
    ])
    assessment_licenses = AssessmentLicenseDetailSerializer(many=True, fields=[
        'uuid', 'count', 'assessment_id', 'users'
    ])
    apprenticeship_licenses = ApprenticeshipLicenseSerializer(many=True, fields=[
        'uuid', 'count', 'apprenticeship_id',
        'users'
    ])

    def get_users(self, obj):
        if obj.company_id:
            return LicenseUserSerializer(UserSettings.objects.filter(customers__in=[obj.company_id]),
                                         many=True).data

    def get_company_name(self, obj):
        if obj.company_id:
            return obj.company_id.name
        return obj.company_id

    def get_superadmin_name(self, obj):
        if obj.superadmin_id:
            return obj.superadmin_id.userName
        return ''

    def get_project_admin_name(self, obj):
        if obj.project_admin:
            return obj.project_admin.userName
        return ''

    def get_company_admin(self, obj):
        if obj.company_admin_id:
            return obj.company_admin_id.userName
        return ''

    def create(self, validated_data):
        try:
            course_licenses = []
            assessment_licenses = []
            apprenticeship_licenses = []

            if 'course_licenses' in validated_data:
                course_licenses = validated_data.pop('course_licenses')
            if 'assessment_licenses' in validated_data:
                assessment_licenses = validated_data.pop('assessment_licenses')
            if 'apprenticeship_licenses' in validated_data:
                apprenticeship_licenses = validated_data.pop('apprenticeship_licenses')

            project = Project.objects.create(**validated_data)
            for data in course_licenses:
                CourseLicense.objects.create(project_id=project, **data)
            for data in assessment_licenses:
                AssessmentLicense.objects.create(project_id=project, **data)
            for data in apprenticeship_licenses:
                ApprenticeshipLicense.objects.create(project_id=project, **data)
            return project
        except Exception as e:
            return super().create(validated_data)

    def update(self, instance, validated_data):
        try:
            course_licenses = []
            assessment_licenses = []
            apprenticeship_licenses = []

            if 'course_licenses' in validated_data:
                course_licenses = validated_data.pop('course_licenses')
            if 'assessment_licenses' in validated_data:
                assessment_licenses = validated_data.pop('assessment_licenses')
            if 'apprenticeship_licenses' in validated_data:
                apprenticeship_licenses = validated_data.pop('apprenticeship_licenses')

            for data in course_licenses:
                cnt = data.pop('count')
                cl, c = CourseLicense.objects.get_or_create(project_id=instance, **data)
                cl.count = cnt
                cl.save()
            for data in assessment_licenses:
                cnt = data.pop('count')
                cl, c = AssessmentLicense.objects.get_or_create(project_id=instance, **data)
                cl.count = cnt
                cl.save()
            for data in apprenticeship_licenses:
                cnt = data.pop('count')
                cl, c = ApprenticeshipLicense.objects.get_or_create(project_id=instance, **data)
                cl.count = cnt
                cl.save()

        except Exception as e:
            pass
        return super().update(instance, validated_data)

