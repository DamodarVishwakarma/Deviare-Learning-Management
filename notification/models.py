from django.db import models
from tools.model_extra import  HTMLField, BaseModel
from django_mysql.models import JSONField
from django.utils import timezone
from tools.email import (send_wrapped_email)
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
# Create your models here.


class EmailTemplate(BaseModel):
    class Meta:
        db_table = 'email_template'
    name = models.CharField(max_length=250)
    body_text = models.TextField(default='', blank=True)
    body_html = HTMLField(default='', blank=True, )
    # attachments = models.ManyToManyField(EmailAttachment, related_name='email_template',  blank=True)

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get(cls, name='ApplicationFormTemplate', just_html=True):
        qs = cls.objects.filter(name=str(name))
        if just_html:
            return qs.values_list('body_html', flat=True).first()
        return qs.values('body_text', 'body_html',).first()


class EmailMessage(models.Model):
    reference = models.CharField(verbose_name='ref', max_length=255, null=True)
    recipient = models.CharField(verbose_name='Recipient Email', max_length=255,null=True)
    subject = models.CharField(verbose_name='Subject', max_length=255,null=True)
    template = models.ForeignKey(EmailTemplate, related_name='messages', on_delete=models.CASCADE)
    content = JSONField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True)
    send_after = models.DateTimeField(auto_now=True, null=True)
    proc_id = models.IntegerField(null=True)

    class Meta:
        verbose_name = "EmailMessage"
        verbose_name_plural = "EmailMessages"

    def __str__(self):
        return f"{self.recipient}, {self.subject}"

    def send(self):
        try:
            sent = send_wrapped_email(
                self.content,
                email_tmpl=self.template.name,
                subject=self.subject,
                recipients=[self.recipient, 'ryan.kanes@deviare.co.za']
            )
            if sent != 0:
                self.sent = True
                self.sent_at = timezone.now()
            self.proc_id = None
            self.save()
        except Exception as e:
            logger.exception(e)

