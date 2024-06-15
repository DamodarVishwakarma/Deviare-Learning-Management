from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.conf import settings
from main.tasks import (create_gcindex_token, delete_gcindex_token)
from main.models import GCIndexAssessment
from main.serializers import (
    GCIndexAssessmentSerializer
)
import json
from notification.models import (EmailMessage, EmailTemplate)
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


def email_gc_user(
        data,
        instance,
        subject='Welcome to your GC Index Assessment',
        template='gcindex_welcome',
        **kw):
    qs = EmailMessage.objects.filter(
        reference=str(instance.uuid),
        subject=subject)
    em = EmailMessage(
        reference=str(instance.uuid),
        recipient=instance.user.email,
        content=json.loads(json.dumps(data, default=str)),
        subject=subject,
        template=EmailTemplate.objects.get(name=template)
    ) if not qs.exists() else qs.first()
    em.save()


def email_gcologist(
        data,
        instance,
        subject='GC Index: New User Notification',
        template='gcindex_notify_new',
        **kw):
    qs = EmailMessage.objects.filter(
        reference=str(instance.uuid),
        subject=subject)
    em = EmailMessage(
        reference=str(instance.uuid),
        recipient=instance.gcologist.email,
        content=json.loads(json.dumps(data, default=str)),
        subject=subject,
        template=EmailTemplate.objects.get(name=template)
    ) if not qs.exists() else qs.first()
    em.save()


def get_gc_email_data(instance):
    ser = GCIndexAssessmentSerializer(instance)
    data = ser.data
    data['url'] = f'{settings.URL}assessments'
    data['gc_url'] = f'{settings.URL}gcindex'
    data['gc_user_url'] = f'{settings.URL}gcindex/{str(instance.uuid)}'
    data['gc_report'] = f'{settings.URL}gcindex/{str(instance.uuid)}/report'
    return data


@receiver(post_save, sender=GCIndexAssessment)
def token_data_received(sender, instance, **kwargs):

    attrs = {}
    update_fields = []
    attrs["uuid"] = instance.uuid
    data = get_gc_email_data(instance)
    if kwargs.get("update_fields", False):
        update_fields = list(kwargs["update_fields"])

    attrs["update_fields"] = update_fields
    attrs["created"] = kwargs["created"]

    if 'gcologist' in update_fields or attrs["created"]:
        if instance.gcologist and not instance.token:
            create_gcindex_token.apply_async(kwargs={'uuid': str(instance.uuid)})
            return
    if 'url' in update_fields:
        if not instance.sent:
            email_gc_user(data, instance)
            email_gcologist(data, instance)

    if 'state' in update_fields:
        if instance.state_id == 8 or instance.report.count() > 0:
            # email_gc_user(data, instance, )
            email_gcologist(data, instance,
                            subject='GC Index: User Complete Notification',
                            template='gcindex_notify_complete')
    if 'deleted' in update_fields:
        if instance.deleted:
            delete_gcindex_token.apply_async(kwargs={'token': str(instance.token)})
        else:
            create_gcindex_token.apply_async(kwargs={'uuid': str(instance.uuid)})
    # on_talent_user.apply_async(kwargs=attrs)
