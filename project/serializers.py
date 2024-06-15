from rest_framework import serializers
from collections import OrderedDict
from tools.rest_extras import (
    DynamicFieldsModelSerializer,
    DataFrameListSerializer
)
from django.db.models import Count, Sum, FieldDoesNotExist, Value as V, BooleanField
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
        fields = ['uuid', 'customer_users', 'role']

    uuid = serializers.SerializerMethodField(read_only=True)
    customer_users = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj:
            return obj.uuid

    def get_customer_users(self, obj):
        if obj:
            return obj.userName


class CourseLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = CourseLicenseUser
        fields = ['user_id', 'uuid', 'customer_users', 'cl_uuid']

    uuid = serializers.SerializerMethodField(read_only=True)
    customer_users = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj.user_id:
            return obj.user_id.uuid

    def get_customer_users(self, obj):
        if obj.user_id:
            return obj.user_id.userName

    def get_cl_uuid(self, obj):
        if obj.course_license_id:
            return obj.course_license_id.uuid


class AssessmentLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicenseUser
        fields = ['user_id', 'uuid', 'customer_users', 'cl_uuid']

    uuid = serializers.SerializerMethodField(read_only=True)
    customer_users = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj.user_id:
            return obj.user_id.uuid

    def get_customer_users(self, obj):
        if obj.user_id:
            return obj.user_id.userName

    def get_cl_uuid(self, obj):
        if obj.assessment_license_id:
            return obj.assessment_license_id.uuid


class ApprenticeshipLicenseUserDetailSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = ApprenticeshipLicenseUser
        fields = ['user_id', 'uuid', 'customer_users', 'cl_uuid']

    uuid = serializers.SerializerMethodField(read_only=True)
    customer_users = serializers.SerializerMethodField(read_only=True)
    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_uuid(self, obj):
        if obj.user:
            return obj.user.uuid

    def get_customer_users(self, obj):
        if obj.user:
            return obj.user.userName

    def get_cl_uuid(self, obj):
        if obj.apprenticeship_license:
            return obj.apprenticeship_license.uuid


class ApprenticeshipLicenseUserDisplaySerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = ApprenticeshipLicenseUser
        fields = ['user_id', 'link', 'name', 'description', 'image', 'batchId']

    link = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    batchId = serializers.SerializerMethodField(read_only=True)

    def get_link(self, obj):
        if obj.apprenticeship_license:
            return obj.apprenticeship_license.apprenticeship.link

    def apprenticeship(self, obj):
        if obj.apprenticeship_license:
            return obj.apprenticeship_license.apprenticeship

    def get_name(self, obj):
        app = self.apprenticeship(obj)
        if obj.details:
            return obj.details.company_name or app.name
        return app.name

    def get_image(self, obj):
        app = self.apprenticeship(obj)
        if obj.details:
            return str(obj.details.company_logo or app.image.url)
        return str(app.image.url)

    def get_description(self, obj):
        app = self.apprenticeship(obj)
        if obj.details:
            return obj.details.description or app.description
        return app.description

    def get_batchId(self, obj):
        if obj.apprenticeship_license:
            return obj.apprenticeship_license.uuid


class BaseLicenseSerializer(serializers.Serializer):

    product_id = serializers.SerializerMethodField(read_only=True)
    product_name = serializers.SerializerMethodField(read_only=True)
    product_type = serializers.SerializerMethodField(read_only=True)
    alloc_users = serializers.SerializerMethodField(read_only=True)
    user_allocation = serializers.SerializerMethodField(read_only=True)
    # users = serializers.SerializerMethodField(method_name='get_user_allocation', read_only=True)
    user_count = serializers.SerializerMethodField(read_only=True)

    cl_uuid = serializers.SerializerMethodField(read_only=True)

    def get_product_id(self, obj):
        return self.product(obj).pk

    def get_product_name(self, obj):
        product = self.product(obj)
        if product:
            return product.name

    def get_product_type(self, obj):
        product = self.product(obj)
        try:
            return product.type
        except Exception as fdne:
            pass
        return product._meta.model_name

    def get_user_count(self, obj):
        if obj.users:
            return obj.users.count()
        return 0

    def get_alloc_users(self, obj):
        if obj.users:
            return obj.users.values_list('user_id', flat=True)
        return []

    def get_user_allocation(self, obj):
        if obj.users:
            return obj.users.annotate(selected=V(True, output_field=BooleanField())).values('uuid', 'user_id',
                                                                                            'selected')
        return []

    def get_cl_uuid(self, obj):
        if obj:
            return obj.uuid


class CourseLicenseDetailSerializer(DynamicFieldsModelSerializer, BaseLicenseSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = CourseLicense
        fields = "__all__"

    users = CourseLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])
    completed_count = serializers.SerializerMethodField(read_only=True)
    course_name = serializers.SerializerMethodField(read_only=True)

    def product(self, obj):
        if obj.course_id:
            return obj.course_id

    def get_completed_count(self, obj):
        if obj.users:
            return obj.users.filter(course_completion__gte=99.99).count()

    def get_course_name(self, obj):
        if obj.course_id:
            return obj.course_id.name


class ApprenticeshipLicenseSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = ApprenticeshipLicense
        fields = "__all__"

    users = ApprenticeshipLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])
    apprenticeship_id = serializers.SerializerMethodField(read_only=True)
    apprenticeship_name = serializers.SerializerMethodField(read_only=True)

    def product(self, obj):
        if obj.apprenticeship:
            return obj.apprenticeship

    def get_apprenticeship_id(self, obj):
        if obj.apprenticeship:
            return obj.apprenticeship.pk

    def get_apprenticeship_name(self, obj):
        if obj.apprenticeship:
            return obj.apprenticeship.name


class AssessmentLicenseDetailSerializer(DynamicFieldsModelSerializer, BaseLicenseSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = AssessmentLicense

        fields = "__all__"

    users = AssessmentLicenseUserDetailSerializer(read_only=True, many=True, fields=['uuid'])
    assessment_name = serializers.SerializerMethodField(read_only=True)

    def product(self, obj):
        if obj.assessment_id:
            return obj.assessment_id

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
        'user_count', 'completed_count', 'cl_uuid', 'uuid', 'count', 'course_id', 'course_name',
        'users'
    ])
    assessment_licenses = AssessmentLicenseDetailSerializer(many=True, fields=[
        'user_count', 'cl_uuid', 'uuid', 'count', 'assessment_id', 'assessment_name',
        'users'
    ])
    apprenticeship_licenses = ApprenticeshipLicenseSerializer(many=True, fields=[
        'user_count', 'cl_uuid', 'uuid', 'count', 'apprenticeship_id', 'apprenticeship_name',
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

