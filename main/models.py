from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password, make_password
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.utils import timezone
from main.fields import SimpleJSONField as JSONField
# from django_mysql.models import JSONField
import uuid
import datetime

from keycloak import keycloak_admin
from keycloak import keycloak_openid

from deviare import settings as deviare_settings
from tools.model_extra import BaseModel, DateModel
from .managers import CourseManager


class UserSettings(BaseModel):
    user = models.ForeignKey(User, related_name='settings', on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, editable=False)
    validated = models.BooleanField(default=False)
    user_id_talentlms = models.CharField(max_length=100, null=True, blank=True)
    firstName = models.CharField(max_length=100, null=True, blank=True)
    lastName = models.CharField(max_length=100, null=True, blank=True)
    userName = models.CharField(max_length=100, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=150, unique=True, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    contact_no = models.BigIntegerField(null=True, blank=True)
    companyID = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="company",
    )
    customers = models.ManyToManyField("Company", blank=True, related_name="customers")
    country = models.CharField(max_length=100, null=True, blank=True)
    profile_image = models.URLField(null=True)
    role = models.CharField(max_length=100, null=True, blank=True)
    last_pw_update_date = models.DateTimeField(null=True, blank=True)
    last_pw_update_by = models.EmailField(max_length=150, null=True, blank=True)
    sub_role = models.CharField(max_length=100, null=True, blank=True)

    @property
    def is_gcologist(self):
        return self.sub_role and self.sub_role == 'gcologist'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self._password = raw_password

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """

        def setter(raw_password):
            self.set_password(raw_password)
            # Password hash upgrades shouldn't be considered password changes.
            self._password = None
            self.save(update_fields=["password"])

        return check_password(raw_password, self.password, setter)

    def __str__(self):
        return self.userName

    @property
    def full_name(self):
        return "%s %s" % (self.firstName.capitalize(), self.lastName.capitalize())

    class Meta:
        db_table = "user_settings"
        verbose_name_plural = "UserSettings"


class Company(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=150, null=True, blank=True)
    contact_no = models.BigIntegerField(null=True)
    logo = models.URLField(null=True)
    branch = models.CharField(max_length=150, default='', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Companies"
        verbose_name = "Company"


# Projects
class Project(BaseModel):
    choices = (("Open", "Open"), ("Complete", "Complete"))

    project_name = models.CharField(max_length=100, null=True, blank=True)
    company_id = models.ForeignKey(Company, related_name='projects', on_delete=models.CASCADE)
    superadmin_id = models.ForeignKey(
        UserSettings, on_delete=models.CASCADE, related_name="project_created_by", null=True
    )
    company_admin_id = models.ForeignKey(
        UserSettings,
        on_delete=models.CASCADE,
        related_name="allocated_admin",
        null=True,
    )
    project_admin = models.ForeignKey(
        UserSettings,
        on_delete=models.CASCADE,
        related_name="allocated_project",
        null=True,
    )
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="Open", choices=choices)
    startDate = models.DateField(auto_now_add=True, null=True)
    endDate = models.DateField(null=True, blank=True)
    is_delete = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.project_name


class ProductState(models.Model):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = "state"

    def __str__(self):
        return '|'.join([str(self.pk), self.name])


# Courses
class Course(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    provider = models.CharField(max_length=30)
    link = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default="Deviare Courses")
    course_id = models.CharField(max_length=30, null=True, blank=True)
    course_type = models.CharField(max_length=30, null=True, blank=True)

    course_id_talent_lms = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    category_id = models.CharField(max_length=10, null=True, blank=True)
    price = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    creation_date = models.CharField(max_length=255, null=True, blank=True)
    last_update_on = models.CharField(max_length=255, null=True, blank=True)
    creator_id = models.CharField(max_length=255, null=True, blank=True)
    hide_from_catalog = models.CharField(max_length=255, null=True, blank=True)
    time_limit = models.CharField(max_length=255, null=True, blank=True)
    level = models.CharField(max_length=255, null=True, blank=True)
    shared = models.CharField(max_length=255, null=True, blank=True)
    shared_url = models.CharField(max_length=255, null=True, blank=True)
    avatar = models.CharField(max_length=255, null=True, blank=True)
    big_avatar = models.CharField(max_length=255, null=True, blank=True)
    certification = models.CharField(max_length=255, null=True, blank=True)
    certification_duration = models.CharField(max_length=255, null=True, blank=True)

    objects = CourseManager()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("course_id", "course_type")


class CourseLicense(BaseModel):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='course_licenses')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_licenses')
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return "%s ~ %s" % (self.project_id, self.course_id.name)


class CourseUserAssignment(BaseModel):
    """
    Model represents courses users have been
    assigned to.
    """
    course = models.ForeignKey(Course, related_name="course", on_delete=models.CASCADE)
    user = models.ForeignKey(UserSettings,
                             related_name="user_assignemt",
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return "%s %s" % (self.course.name, self.user.user.email)


class CourseLicenseUser(BaseModel):
    course_license_id = models.ForeignKey(CourseLicense, on_delete=models.CASCADE, related_name='users')
    user_id = models.ForeignKey(UserSettings, on_delete=models.CASCADE, related_name='registered_courses')
    course_completion = models.FloatField(null=True)

    def __str__(self):
        return "%s ~ %s" % (self.course_license_id.course_id.name, self.user_id.email)


def image_directory_path(instance, filename):
    return f"{instance.name.replace(' ', '_')}/im_{filename}"


# Assessments
class Assessment(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.CharField(max_length=30)
    link = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class AssessmentLicense(BaseModel):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assessment_licenses')
    assessment_id = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='assessment_licenses')
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return "%s ~ %s" % (self.project_id.project_name, self.assessment_id.name)


class AssessmentLicenseUser(BaseModel):
    assessment_license_id = models.ForeignKey(
        AssessmentLicense, on_delete=models.CASCADE, related_name='users'
    )
    user_id = models.ForeignKey(UserSettings, null=True, on_delete=models.CASCADE,
                                related_name='registered_assessments')

    def __str__(self):
        return "%s %s " % (self.assessment_license_id, self.user_id.email)


# Apprenticeships
class Apprenticeship(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default='', null=True)
    duration = models.CharField(max_length=150, null=True)
    link = models.TextField(null=True)
    image = models.ImageField(upload_to=image_directory_path, null=True)

    def __str__(self):
        return self.name


class ApprenticeshipLicense(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='apprenticeship_licenses')
    apprenticeship = models.ForeignKey(Apprenticeship, on_delete=models.CASCADE, related_name='apprenticeship_licenses')
    count = models.IntegerField(default=1, null=True)

    def __str__(self):
        return "%s ~ %s" % (self.project.project_name, self.apprenticeship.name)


class ApprenticeshipDetails(BaseModel):
    company_logo = models.TextField(null=True)
    company_name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


class ApprenticeshipLicenseUser(BaseModel):
    apprenticeship_license = models.ForeignKey(
        ApprenticeshipLicense,
        on_delete=models.CASCADE,
        related_name='users'
    )
    user = models.ForeignKey(
        UserSettings,
        null=True,
        on_delete=models.CASCADE,
        related_name='registered_apprenticeships'
    )
    details = models.ForeignKey(
        ApprenticeshipDetails,
        null=True,
        on_delete=models.CASCADE,
        related_name='apprentices'
    )

    def __str__(self):
        return "%s %s " % (self.apprenticeship_license, self.user.email)


# Experiments
class Experiment(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    link = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class ExperimentLicense(BaseModel):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    experiment_id = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    count = models.IntegerField()


class ExperimentLicenseUser(BaseModel):
    experiment_license_id = models.ForeignKey(
        ExperimentLicense, on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


# Deployments
class Deployment(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    repository = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class DeploymentLicense(BaseModel):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    deployment_id = models.ForeignKey(Deployment, on_delete=models.CASCADE)
    count = models.IntegerField()


class DeploymentLicenseUser(BaseModel):
    deployment_license_id = models.ForeignKey(
        DeploymentLicense, on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Theme(BaseModel):
    company = models.ForeignKey(Company, related_name='theme', on_delete=models.CASCADE)
    config = JSONField(blank=True, null=True)
    sub_domain = models.CharField(blank=True, max_length=100, null=True)


class TMForumDimension(BaseModel):
    title = models.CharField(blank=True, max_length=255, null=True)
    value = models.IntegerField(null=True)

    class Meta:
        ordering = ['value']
        db_table = "tmforum_dimension"

    def __str__(self):
        return self.title


class TMForumSubDimension(BaseModel):
    dimension = models.ForeignKey(TMForumDimension, related_name='subDimensions', on_delete=models.CASCADE)
    value = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=255, null=True)
    description = models.TextField(blank=True, max_length=255, null=True)

    class Meta:
        ordering = ['value']
        db_table = "tmforum_sub_dimension"

    def __str__(self):
        return "%s ~ %s" % (self.dimension.title, self.title)


class TMForumCriterion(BaseModel):
    sub_dimension = models.ForeignKey(TMForumSubDimension, related_name='criteria', on_delete=models.CASCADE)
    value = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=255, null=True)
    description = models.TextField(blank=True, max_length=255, null=True)

    class Meta:
        ordering = ['value']
        db_table = "tmforum_criterion"


class TMForumRatingDetail(BaseModel):
    criterion = models.ForeignKey(TMForumCriterion, related_name='rating_details', on_delete=models.CASCADE)
    value = models.IntegerField(null=True)
    title = models.CharField(blank=True, max_length=255, null=True)
    description = models.TextField(blank=True, max_length=255, null=True)

    class Meta:
        db_table = "tmforum_rating_detail"


class TMForumUserResponse(BaseModel):
    owner = models.ForeignKey(UserSettings, related_name='tmforum_assessment_responses', on_delete=models.CASCADE)
    criterion = models.ForeignKey(TMForumCriterion, null=True, related_name='user_responses', on_delete=models.SET_NULL)
    aspiration = models.ForeignKey(TMForumRatingDetail, null=True, related_name='user_aspiration',
                                   on_delete=models.SET_NULL)
    status_quo = models.ForeignKey(TMForumRatingDetail, null=True, related_name='user_status_quo',
                                   on_delete=models.SET_NULL)
    comment = models.TextField(blank=True, null=True)
    document = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "tmforum_user_response"
        unique_together = ('owner', 'criterion')

    def auto_assign(self):
        if self.assigned.all().count() == 0:
            t = TMForumUserAssessment.objects.using('default').filter(
                owner=self.owner, sub_dimension=self.criterion.sub_dimension
            ).first()
            t.responses.add(self)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     # self.auto_assign()
    #     super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return "%s %s " % (self.owner.email, self.criterion.title)


class TMForumUserAssessment(BaseModel):
    owner = models.ForeignKey(UserSettings, related_name='tmforum_assessment_criteria', on_delete=models.CASCADE)
    sub_dimension = models.ForeignKey(TMForumSubDimension, null=True, related_name='user_assessment',
                                      on_delete=models.CASCADE)
    responses = models.ManyToManyField(TMForumUserResponse, related_name='assigned')

    class Meta:
        db_table = "tmforum_user_assessement"
        # unique_together = ('owner', 'sub_dimension')

    def auto_update(self):
        self.responses.set(TMForumUserResponse.objects.filter(
            owner=self.owner,
            criterion__in=self.sub_dimension.criteria.values_list('uuid'))
        )

    @classmethod
    def get_or_create(cls, **kw):
        qs = cls.objects.filter(**kw)
        if qs.exists():
            return qs.first(), False
        return cls(**kw), True

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     # self.auto_update()
    #     super().save(force_insert, force_update, using, update_fields)


class TMForumAssignedAssessment(BaseModel):
    # course_license_user = models.ForeignKey(CourseLicenseUser, null=True, related_name='tmforum_assessment',
    #                                         on_delete=models.CASCADE)
    owner = models.ForeignKey(UserSettings, related_name='tmforum_assessment', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, null=True, related_name='tmforum_assessment', on_delete=models.CASCADE)
    assessment = models.ManyToManyField(TMForumUserAssessment, related_name='assigned', )

    class Meta:
        db_table = "tmforum_assigned_assessement"


class UserReport(BaseModel):
    """
    Model instance stores user reports
    """
    user_license = models.ForeignKey(CourseLicenseUser, related_name='user_report', on_delete=models.CASCADE)
    report = JSONField(blank=True, null=True)


class Role(DateModel):
    name = models.CharField(blank=True, max_length=255, null=True)
    lms = models.CharField(blank=True, max_length=255, null=True)
    human_readable = models.CharField(blank=True, max_length=255, null=True)

    class Meta:
        db_table = "role"


class MenuItem(DateModel):
    parent = models.ForeignKey('main.MenuItem', related_name='children', on_delete=models.CASCADE)
    icon = models.CharField(blank=True, max_length=255, null=True)
    title = models.CharField(blank=True, max_length=255, null=True)
    path = models.CharField(blank=True, max_length=255, null=True)
    component = models.TextField(blank=True, null=True)
    role = models.ManyToManyField(Role, related_name='menu')

    class Meta:
        db_table = "menu_item"

    @classmethod
    def for_role(cls, role_name='user'):
        return cls.objects.filter(role__name=role_name)


class GCState(models.Model):
    """
    Awaiting GCologist
    Awaiting Token
    Assessment Sent
    Assessment Completed
    Assessment Report Ready for Review
    Assessment Reviewed

    """
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        db_table = "gcstate"

    def __str__(self):
        return self.name


class GCIndexAssessment(BaseModel):
    user = models.ForeignKey(UserSettings, related_name='gcindex', on_delete=models.CASCADE)
    gcologist = models.ForeignKey(UserSettings, related_name='gcindex_users', null=True, on_delete=models.CASCADE)
    state = models.ForeignKey(GCState, related_name='gcindex', null=True, on_delete=models.CASCADE)
    token = models.TextField(blank=True, null=True)
    url = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False, null=True)
    completed_at = models.DateTimeField(null=True)
    has_report = models.BooleanField(default=False, null=True)
    sent = models.BooleanField(default=False, null=True)
    deleted = models.BooleanField(default=False, null=True)

    class Meta:
        db_table = "gcindex_assessment"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        changes = {}
        update_fields = []
        if not self._state.adding:
            # We have an update
            cls = self.__class__
            old = cls.objects.get(pk=self.pk)
            new = self
            changed_fields = []

            for field in cls._meta.get_fields():
                field_name = field.name
                try:
                    if getattr(old, field_name) != getattr(new, field_name):
                        changed_fields.append(field_name)
                        if field_name == 'state':
                            changes[field_name] = getattr(old, field_name)
                except Exception as exc:
                    pass
            update_fields = changed_fields
        if not self.gcologist:
            self.state = GCState.objects.get(name='Awaiting GCologist')
        else:
            # if not update_fields:
            if self._state.adding:
                self.state_id = 1
            if not self.token and self.state_id == 1:
                self.state_id = 2
                if not self._state.adding:
                    update_fields.append('state')
            else:
                if 'state' not in changes.keys():
                    self.state_id = 3
                    if not self._state.adding:
                        update_fields.append('state')
            if not self._state.adding:
                if 'state' not in changes.keys():
                    if self.url and self.state_id in [2, 3]:
                        self.state_id = 4
                        update_fields.append('state')
                    if self.sent and self.state_id < 5:
                        self.state_id = 5
                        update_fields.append('state')
                    if self.completed and (self.state_id == 10 or self.state_id < 6):
                        self.state_id = 6
                        update_fields.append('state')
                    elif self.has_report:
                        if str(changes.get('state', '')) == 'Assessment Completed' or self.state_id < 7:
                            self.state_id = 7
                            update_fields.append('state')
                update_fields = list(set(update_fields))
        super().save(force_insert, force_update, using, update_fields)


class GCIndexReport(BaseModel):
    assessment = models.ForeignKey(GCIndexAssessment, related_name='report', on_delete=models.CASCADE)
    report = models.BinaryField(null=True)
    report_data = JSONField(null=True)


class GCIndexAssessmentTrack(DateModel):
    assessment = models.ForeignKey(GCIndexAssessment, related_name='track', on_delete=models.CASCADE)
    state = models.ForeignKey(GCState, related_name='track', null=True, on_delete=models.CASCADE)
    updated_fields = JSONField(null=True, default=list)


class ElearninStates(models.Model):
    updated_at = models.DateTimeField(auto_now=True, null=True)
    name = models.CharField(max_length=120, null=True, blank=True)
    email = models.EmailField(unique=True)
    account_status = models.CharField(max_length=90, blank=True,null=True)
    order_type = models.CharField(max_length=90, blank=True, null=True)
    team = models.CharField(max_length=220, blank=True, null=True, default='NA')
    course_assignment_date = models.DateTimeField(null=True, blank=True)
    course_activation_date = models.DateTimeField(null=True, blank=True)
    course_type = models.CharField(max_length=90, blank=True, null=True)
    course_id = models.IntegerField(null=True)
    self_learning_completion = models.FloatField(null=True)
    course_expiration_date = models.DateTimeField(null=True, blank=True)
    course_title = models.CharField(max_length=500, blank=True, null=True)
    test_score = models.FloatField(null=True)  # not done
    project_result = models.CharField(max_length=70, blank=True, null=True)
    course_completion_date = models.DateTimeField(null=True)
    live_class_attended = models.IntegerField(null=True)  # Learning days
    osl_score = models.FloatField(null=True)  # not done
    lvc_sore = models.FloatField(null=True)  # not done
    project_score = models.IntegerField(null=True)  # not done
    test_score = models.FloatField(null=True)  # not done
    certification_score = models.FloatField(null=True)
    concat = models.CharField(max_length=200, null=True)  # email+course_id
    program = models.CharField(max_length=200, null=True)  # course name
    certification_status = models.CharField(max_length=225,
                                            null=True)  # from course completion date ( is date is available then certified else not Certified

    # course_activity_level = models.CharField(max_length=500,null=True)
    # live_class_registered = models.IntegerField(null=True)
    # live_class_attended = models.IntegerField(null=True)
    # course_test = models.CharField(max_length=225,null=True)
    # course_project = models.CharField(max_length=225,null=True)
    # course_inprogress_status = models.CharField(max_length=225,null=True)
    # course_activation = models.CharField(max_length=225,null=True)
    # course_learning_path = models.CharField(max_length=225,null=True)
    # course_elearning_status = models.CharField(max_length=225,null=True)
    # elearning_score = models.FloatField(null=True)
    # course_completion_score = models.FloatField(null=True)
    # project_score = models.FloatField(null=True)
    # overall_score = models.FloatField(null=True)
    # overall_rank = models.IntegerField(null=True)
    # elearning_template_id = models.IntegerField(null=True)
    # user_id = models.IntegerField(null=True)


def prepare_list(state: ElearninStates):
    name = state.email # should be coming from user foreignkey
    learner_email = state.email # should be coming from user foreignkey
    account_status = state.account_status
    order_type = state.order_type
    team = None
    course_assignment_date = state.course_assignment_date
    course_activation_date = state.course_activation_date
    course_type = 'Self Placed' if state.course_title.startswith('Introduction') else 'Online classroom'
    course_id = state.course_id
    course_title = state.course_title
    self_paced_learnign_percent = state.self_learning_completion
    course_completion_date = state.course_completion_date
    test_score = state.test_score #todo
    project_result = 1 #todo
    live_class_attendance = state.live_class_attended
    osl_score = state #todo
    lvc_score = state.live_class_attended #todo
    project_score = state.project_score # todo
    test_score_percent = state.project_score # todo
    certification_score = 0 if course_activation_date else 50
    concat = state.email + str(state.course_id )# todo
    program = state.course_title
    learner_name = state.name # todo
    total_score = state.project_score # todo
    certification_status =  'Certified' if state.course_completion_date else 'Not Certified'
    learning_path = 1 #todo





