from rest_framework import serializers
from collections import OrderedDict
from tools.rest_extras import DynamicFieldsModelSerializer, DataFrameListSerializer
from django.db.models import Q, F, Value as V, Count, Sum
from main.models import (
    Company,
    UserSettings,
    Course,
    Project,
    CourseLicense,
    AssessmentLicense,
    CourseLicenseUser,
    Assessment,
    Experiment,
    Deployment,
    CourseUserAssignment,
    TMForumDimension,

    TMForumSubDimension,
    TMForumCriterion,
    TMForumRatingDetail,

    TMForumUserAssessment,
    TMForumAssignedAssessment,
    TMForumUserResponse,
    GCState,
    GCIndexAssessment,
    GCIndexReport
)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = "__all__"


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = "__all__"


class DeploymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deployment
        fields = "__all__"


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


class CourseLicenseDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLicense
        fields = "__all__"
    consumed_licenses = serializers.SerializerMethodField(read_only=True)
    completed_count = serializers.SerializerMethodField(read_only=True)

    def get_consumed_licenses(self, obj):
        if obj.users:
            return obj.users.count()

    def get_completed_count(self, obj):
        if obj.users:
            return obj.users.filter(course_completion_gte=99.99).count()


class AssessmentLicenseDashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentLicense
        fields = "__all__"

    consumed_licenses = serializers.SerializerMethodField(read_only=True)

    def get_consumed_licenses(self, obj):
        if obj.users:
            return obj.users.count()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['uuid', 'role', 'userName']


class ProjectSummarySerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = Project
        fields = "__all__"

    company_name = serializers.SerializerMethodField(read_only=True)
    project_admin_name = serializers.SerializerMethodField(read_only=True)
    company_admin_name = serializers.SerializerMethodField(read_only=True)
    superadmin_name = serializers.SerializerMethodField(read_only=True)
    total_course_licenses = serializers.SerializerMethodField(read_only=True)
    consumed_course_licenses = serializers.SerializerMethodField(read_only=True)
    course_completed_count = serializers.SerializerMethodField(read_only=True)

    total_assessment_licenses = serializers.SerializerMethodField(read_only=True)
    consumed_assessment_licenses = serializers.SerializerMethodField(read_only=True)

    total_licenses = serializers.SerializerMethodField(read_only=True)
    total_license_count = serializers.SerializerMethodField(read_only=True)

    total_course = serializers.SerializerMethodField(read_only=True)

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

    def get_company_admin_name(self, obj):
        if obj.company_admin_id:
            return obj.company_admin_id.userName
        return ''

    def get_total_course_licenses(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().aggregate(Sum('count')).get('count__sum', 0)
        return 0

    def get_consumed_course_licenses(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().annotate(
                tot=Count('users__uuid', distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    def get_total_course(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.count()
        return 0

    def get_course_completed_count(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().annotate(
                tot=Count('users__uuid',
                          filter=Q(users__course_completion__gte=99.99),
                          distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    def get_total_assessment_licenses(self, obj):
        if obj.assessment_licenses.exists():
            return obj.assessment_licenses.all().aggregate(Sum('count')).get('count__sum', 0)
        return 0

    def get_consumed_assessment_licenses(self, obj):
        if obj.assessment_licenses.exists():
            return obj.assessment_licenses.all().annotate(
                tot=Count('users__uuid', distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    # def get_total_project
    def get_user_count(self, obj):
        return obj.course_licenses.values_list('users__uuid', flat=True).union(
            obj.assessment_licenses.values_list('users__uuid', flat=True)).distinct().count()

    def get_total_licenses(self, obj):
        return self.get_consumed_assessment_licenses(obj) + self.get_consumed_course_licenses(obj)

    def get_total_license_count(self, obj):
        return self.get_total_assessment_licenses(obj) + self.get_total_course_licenses(obj)


class ProjectDashboardSerializer(DynamicFieldsModelSerializer):
    class Meta:
        list_serializer_class = DataFrameListSerializer
        model = Project
        fields = "__all__"
    project_admin = UserSimpleSerializer()
    company_admin_id = UserSimpleSerializer()
    superadmin_id = UserSimpleSerializer()

    user_count = serializers.SerializerMethodField(read_only=True)
    total_users = serializers.SerializerMethodField(read_only=True)
    total_course_licenses = serializers.SerializerMethodField(read_only=True)
    consumed_course_licenses = serializers.SerializerMethodField(read_only=True)
    course_completed_count = serializers.SerializerMethodField(read_only=True)

    total_assessment_licenses = serializers.SerializerMethodField(read_only=True)
    consumed_assessment_licenses = serializers.SerializerMethodField(read_only=True)

    total_licenses = serializers.SerializerMethodField(read_only=True)
    total_license_count = serializers.SerializerMethodField(read_only=True)

    def get_total_course_licenses(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().aggregate(Sum('count')).get('count__sum', 0)
        return 0

    def get_consumed_course_licenses(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().annotate(
                tot=Count('users__uuid', distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    def get_course_completed_count(self, obj):
        if obj.course_licenses.exists():
            return obj.course_licenses.all().annotate(
                tot=Count('users__uuid',
                          filter=Q(users__course_completion__gte=99.99),
                          distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    def get_total_assessment_licenses(self, obj):
        if obj.assessment_licenses.exists():
            return obj.assessment_licenses.all().aggregate(Sum('count')).get('count__sum', 0)
        return 0

    def get_consumed_assessment_licenses(self, obj):
        if obj.assessment_licenses.exists():
            return obj.assessment_licenses.all().annotate(
                tot=Count('users__uuid', distinct=True)
            ).values_list('tot', flat=True)[0]
        return 0

    def get_total_users(self, obj):
        return obj.company_id.company.all().count()

    def get_user_count(self, obj):
        return obj.course_licenses.values_list('users__uuid', flat=True).union(
            obj.assessment_licenses.values_list('users__uuid', flat=True)).distinct().count()

    def get_total_licenses(self, obj):
        return self.get_consumed_assessment_licenses(obj) + self.get_consumed_course_licenses(obj)

    def get_total_license_count(self, obj):
        return self.get_total_assessment_licenses(obj) + self.get_total_course_licenses(obj)





class CourseLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLicense
        fields = "__all__"


class CourseLicenseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseLicenseUser
        fields = "__all__"


class CourseUserAssignmentSerializer(serializers.Serializer):

    course_id = serializers.CharField(max_length=255, allow_blank=False)
    email = serializers.EmailField(max_length=255, allow_blank=False)


ratingTitles = {
    "1": "Initiating",
    "2": "Emerging",
    "3": "Performing",
    "4": "Advancing",
    "5": "Leading",
}


class TMForumRatingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumRatingDetail
        # fields = ['uuid', 'criterion', 'attributeID', 'description',  'title', 'ratingValue']
        # fields = "__all__"
        include = '__all__'
        exclude = ['created_at', 'updated_at']

    attributeID = serializers.SerializerMethodField(read_only=True)
    # ratingTitle = serializers.SerializerMethodField(read_only=True)
    # ratingValue = serializers.SerializerMethodField(read_only=True)

    def get_attributeID(self, obj):
        if obj.criterion:
            return f'{obj.criterion.sub_dimension.dimension.value}.{obj.criterion.sub_dimension.value}.{obj.criterion.value}.{obj.value}'
        return obj.value

    # def get_ratingTitle(self, obj):
    #     return ratingTitles[f'{obj.value}']
    #
    # def get_ratingValue(self, obj):
    #     return obj.value


class TMForumCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumCriterion
        # fields = ['uuid', 'criteriaID', 'shortLabel', 'criteriaLabel', 'description', 'ratingExplained']
        # fields = "__all__"
        include = '__all__'
        exclude = ['created_at', 'updated_at']

    # shortLabel = serializers.SerializerMethodField(read_only=True)
    criteriaID = serializers.SerializerMethodField(read_only=True)
    attrs = serializers.SerializerMethodField(read_only=True)
    # criteriaLabel = serializers.SerializerMethodField(read_only=True)
    path = serializers.SerializerMethodField(read_only=True)

    def get_path(self, obj):
        if obj.sub_dimension:
            return f'/tmforum/{obj.sub_dimension.dimension.value}/{obj.sub_dimension.value}/{obj.value}/'
        return obj.value

    # def get_criteriaLabel(self, obj):
    #     return obj.description
    #
    # def get_shortLabel(self, obj):
    #     return obj.title

    def get_criteriaID(self, obj):
        if obj.sub_dimension:
            return f'{obj.sub_dimension.dimension.value}.{obj.sub_dimension.value}.{obj.value}'
        return obj.value

    def get_attrs(self, obj):
        if obj.rating_details:
            return TMForumRatingDetailSerializer(obj.rating_details, many=True).data
        return obj.rating_details


class TMForumSubDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumSubDimension
        # fields = ['uuid', 'subDimensionID', 'name', 'description', 'criteria']
        # fields = "__all__"
        include = '__all__'
        exclude = ['created_at', 'updated_at']

    subDimensionID = serializers.SerializerMethodField(read_only=True)
    criteria = serializers.SerializerMethodField(read_only=True)
    # name = serializers.SerializerMethodField(read_only=True)
    path = serializers.SerializerMethodField(read_only=True)

    def get_path(self, obj):
        if obj.dimension:
            return f'/tmforum/{obj.dimension.value}/{obj.value}/'
        return obj.value

    # def get_name(self, obj):
    #     return obj.title

    def get_subDimensionID(self, obj):
        if obj.dimension:
            return f'{obj.dimension.value}.{obj.value}'
        return obj.value

    def get_criteria(self, obj):
        if obj.criteria:
            return TMForumCriterionSerializer(obj.criteria.order_by('value'), many=True).data
        return obj.criteria


class TMForumDimensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumDimension
        # fields = ['uuid', 'formNumber', 'dimensionTitle', 'subDimensions']
        include = '__all__'
        exclude = ['created_at', 'updated_at']
    # formNumber = serializers.SerializerMethodField(read_only=True)
    # dimensionTitle = serializers.SerializerMethodField(read_only=True)
    subDimensions = serializers.SerializerMethodField(read_only=True)
    path = serializers.SerializerMethodField(read_only=True)

    def get_path(self, obj):
        if obj.value:
            return f'/tmforum/{obj.value}/'
        return obj.value

    def get_subDimensions(self, obj):
        return TMForumSubDimensionSerializer(obj.subDimensions.order_by('value'), many=True).data


class TMForumUserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumUserResponse
        fields = "__all__"


def toID(arr, delim='.'):
    return delim.join(list(map(str, arr)))


class TMForumUserResponseDocSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = TMForumUserResponse
        fields = "__all__"
    # ['dimension', 'sub_dimension', 'sub_dimension_description',
    # 'criterion', 'status_quo', 'aspiration', 'comment', ]

    rename = OrderedDict([
        ('dimension_id', 'Dimension ID'),
        ('dimension', 'Dimension'),
        # ('dimension_description', 'Dimension Description'),

        ('sub_dimension_id', 'Sub-Dimension ID'),
        ('sub_dimension', 'Sub-Dimension'),
        ('sub_dimension_description', 'Sub-Dimension Description'),

        ('criterion_id', 'Criteria ID'),
        ('criterion', 'Criteria'),

        ('status_quo_id', 'Status Quo ID'),
        ('status_quo', 'Status Quo'),
        ('status_quo_value', 'Status Quo Value'),

        ('aspiration_id', 'Aspiration ID'),
        ('aspiration', 'Aspiration'),
        ('aspiration_value', 'Aspiration Value'),

        ('comment', 'Comment'),
    ])
    dimension_id = serializers.SerializerMethodField(read_only=True)
    dimension = serializers.SerializerMethodField(read_only=True)
    # dimension_description = serializers.SerializerMethodField(read_only=True)

    sub_dimension_id = serializers.SerializerMethodField(read_only=True)
    sub_dimension = serializers.SerializerMethodField(read_only=True)
    sub_dimension_description = serializers.SerializerMethodField(read_only=True)

    criterion_id = serializers.SerializerMethodField(read_only=True)
    criterion = serializers.SerializerMethodField(read_only=True)

    status_quo_id = serializers.SerializerMethodField(read_only=True)
    status_quo = serializers.SerializerMethodField(read_only=True)
    status_quo_value = serializers.SerializerMethodField(read_only=True)

    aspiration_id = serializers.SerializerMethodField(read_only=True)
    aspiration = serializers.SerializerMethodField(read_only=True)
    aspiration_value = serializers.SerializerMethodField(read_only=True)

    def get_dimension(self, obj):
        if obj.criterion:
            return obj.criterion.sub_dimension.dimension.title
        return obj.criterion

    def get_dimension_id(self, obj):
        if obj.criterion:
            return toID([
                obj.criterion.sub_dimension.dimension.value,
            ])
        return obj.criterion

    # def get_dimension_description(self, obj):
    #     if obj.criterion:
    #         return toID([
    #             obj.criterion.sub_dimension.dimension.description,
    #         ])
    #     return obj.criterion

    def get_sub_dimension(self, obj):
        if obj.criterion:
            return obj.criterion.sub_dimension.title
        return obj.criterion

    def get_sub_dimension_id(self, obj):
        if obj.criterion:
            return toID([
                self.get_dimension_id(obj),
                obj.criterion.sub_dimension.value,
            ])
        return obj.criterion

    def get_sub_dimension_description(self, obj):
        if obj.criterion:
            return obj.criterion.sub_dimension.description
        return obj.criterion

    def get_criterion(self, obj):
        if obj.criterion:
            return obj.criterion.title
        return obj.criterion

    def get_criterion_id(self, obj):
        if obj.criterion:
            return toID([
                self.get_sub_dimension_id(obj),
                obj.criterion.value,
            ])
        return obj.criterion

    def get_status_quo_id(self, obj):
        if obj.status_quo:
            return toID([
                self.get_criterion_id(obj),
                obj.status_quo.value,
            ])
        return obj.status_quo

    def get_status_quo(self, obj):
        if obj.status_quo:
            return obj.status_quo.title
        return obj.status_quo

    def get_status_quo_value(self, obj):
        if obj.status_quo:
            return obj.status_quo.value
        return obj.status_quo

    def get_aspiration_id(self, obj):
        if obj.aspiration:
            return toID([
                self.get_criterion_id(obj),
                obj.aspiration.value,
            ])
        return obj.aspiration

    def get_aspiration(self, obj):
        if obj.aspiration:
            return obj.aspiration.title
        return obj.aspiration

    def get_aspiration_value(self, obj):
        if obj.aspiration:
            return obj.aspiration.value
        return obj.aspiration


class TMForumUserAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumUserAssessment
        fields = "__all__"


class TMForumUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumUserAssessment
        fields = "__all__"

    dimension = serializers.SerializerMethodField(read_only=True)
    incomplete = serializers.SerializerMethodField(read_only=True)
    complete = serializers.SerializerMethodField(read_only=True)
    total = serializers.SerializerMethodField(read_only=True)

    def get_dimension(self, obj):
        if obj.sub_dimension:
            return obj.sub_dimension.dimension.uuid
        return obj.sub_dimension

    def get_total(self, obj):
        if obj.sub_dimension:
            return obj.sub_dimension.criteria.all().count()
        return obj.sub_dimension

    def get_incomplete(self, obj):
        if obj.responses:
            return self.get_total(obj) - self.get_complete(obj)
        return obj.responses

    def get_complete(self, obj):
        if obj.responses:
            return obj.responses.filter(status_quo__isnull=False, aspiration__isnull=False,).count()
        return obj.responses


class TMForumAssignedAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumAssignedAssessment
        fields = "__all__"

    assessment = TMForumUserSerializer(many=True)


class TMForumUserResponseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TMForumUserResponse
        fields = "__all__"


class UserProgressReportSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    course_id = serializers.UUIDField()


class CustomerDigitalReadinessReportSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()


class UserLearningPathReportSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    project_id = serializers.UUIDField()


class GCStateSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = GCState
        fields = ['id', 'name']


class GCIndexAssessmentSerializer(DynamicFieldsModelSerializer):
    class Meta:
        # list_serializer_class = DataFrameListSerializer
        model = GCIndexAssessment
        fields = "__all__"

    report_available = serializers.SerializerMethodField(read_only=True)
    state_id = serializers.SerializerMethodField(read_only=True)
    userName = serializers.SerializerMethodField(read_only=True)
    firstname = serializers.SerializerMethodField(read_only=True)
    lastname = serializers.SerializerMethodField(read_only=True)
    gcologist_firstname = serializers.SerializerMethodField(read_only=True)
    gcologist_lastname = serializers.SerializerMethodField(read_only=True)
    gcologistName = serializers.SerializerMethodField(read_only=True)
    state_name = serializers.SerializerMethodField(read_only=True)

    def get_report_available(self, obj):
        if obj.report:
            return obj.report.count() > 0
        return False

    def get_state_id(self, obj):
        if obj.state_id:
            return obj.state_id
        return 1

    def get_state_name(self, obj):
        if obj.state:
            return obj.state.name
        return 'Unknown'

    def get_userName(self, obj):
        if obj.user:
            return obj.user.userName
        return obj.user

    def get_gcologistName(self, obj):
        if obj.gcologist:
            return obj.gcologist.userName
        return obj.gcologist

    def get_firstname(self, obj):
        if obj.user:
            return obj.user.firstName
        return obj.user

    def get_lastname(self, obj):
        if obj.user:
            return obj.user.lastName
        return obj.user

    def get_gcologist_firstname(self, obj):
        if obj.gcologist:
            return obj.gcologist.firstName
        return obj.gcologist

    def get_gcologist_lastname(self, obj):
        if obj.gcologist:
            return obj.gcologist.lastName
        return obj.gcologist

    def create(self, validated_data):
        try:
            if 'state' in validated_data:
                state = validated_data.get('state', 1)
                if not isinstance(state, GCState):
                    validated_data.pop('state')
                    validated_data['state_id'] = state
        except Exception as e:
            print(e)
            pass
        return super().create(validated_data)


class GCIndexReportSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = GCIndexReport
        fields = "__all__"
