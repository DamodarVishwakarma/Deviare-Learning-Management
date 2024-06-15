
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.db import models
from django.db.models import PROTECT
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class LmsType(models.Model):
    name = models.CharField(unique=True, db_index=True, default='', max_length=100)

    class Meta:
        verbose_name = "LMS Type"
        verbose_name_plural = "LMS Types"

    def __str__(self):
        return f"{self.name}"


class TimelineAction(models.Model):
    name = models.CharField(unique=True, db_index=True, default='', max_length=100)
    # lms_type = models.CharField(default='', db_index=True, max_length=100)
    verbose_name = models.CharField(default='', max_length=100)

    class Meta:
        verbose_name = "Timeline Action"
        verbose_name_plural = "Timeline Actions"

    def __str__(self):
        return f"{self.name}"


class Timeline(models.Model):
    action = models.ForeignKey(TimelineAction, related_name='events', null=True, on_delete=models.CASCADE)
    message = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('main.UserSettings',
                             # to_field='user_id_talentlms',
                             related_name='lms_events',
                             null=True, on_delete=models.CASCADE)
    object = models.CharField(default='-', max_length=10)
    object_name = models.CharField(default='-', max_length=150)
    secondary_object = models.CharField(default='-', max_length=10)
    secondary_object_name = models.CharField(default='-', max_length=150)
    event_counter = models.CharField(default='1', max_length=10)

    class Meta:
        verbose_name = "Timeline"
        verbose_name_plural = "Timelines"

    def __str__(self):
        return f"{self.message}"

