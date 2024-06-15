from django.contrib import admin
from .models import (EmailTemplate, EmailMessage)
from django.conf.urls import url
# Register your models here.


admin.site.register(EmailTemplate, )
admin.site.register(EmailMessage, )