from django.contrib import admin
from django.db import models
from django.conf.urls import url
from main.models import UserSettings, Company, Project, Course, Assessment, Experiment, Deployment, Course
from .models import (
    Course,
    UserSettings,
    CourseUserAssignment,
    CourseLicense,
    CourseLicenseUser,
    Project,
    Assessment,
    AssessmentLicense,
    AssessmentLicenseUser,
    Apprenticeship,
    Company,
    UserReport, ElearninStates)
from main import views


class BaseModelAdmin(admin.ModelAdmin):
    readonly_fields = ('uuid', 'created_at', 'updated_at',)


class BaseUserAdmin(BaseModelAdmin):
    search_fields = ('email', )


class BaseCourseAdmin(BaseModelAdmin):
    search_fields = ('name', 'course_id_talent_lms', 'course_id', )


# Update Records
class UpdateRecords(models.Model):

    class Meta:
        verbose_name_plural = 'UpdateRecords'
        app_label = 'main'


def my_custom_view(request):
    return views.read_mail_api(request)


class UpdateRecordsAdmin(admin.ModelAdmin):
    model = UpdateRecords

    def get_urls(self):
        view_name = '{}_{}_changelist'.format(self.model._meta.app_label, self.model._meta.model_name)
        return [url('my_admin_path/', my_custom_view, name=view_name)]


admin.site.register(UpdateRecords, UpdateRecordsAdmin)

admin.site.register(Course, BaseCourseAdmin)
admin.site.register(UserSettings, BaseUserAdmin)
admin.site.register(CourseUserAssignment)
admin.site.register(Company)
admin.site.register(CourseLicense)
admin.site.register(CourseLicenseUser)
admin.site.register(Project)
admin.site.register(Assessment)
admin.site.register(AssessmentLicense)
admin.site.register(AssessmentLicenseUser)
admin.site.register(Apprenticeship)
admin.site.register(UserReport)
admin.site.register(ElearninStates)