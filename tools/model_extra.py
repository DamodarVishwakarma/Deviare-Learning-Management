import datetime
import uuid
import pytz
from django.db.models import TextField as HTMLField
from django.db import models


class BaseModelUuid(models.Model):
    class Meta:
        abstract = True
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class DateModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_seconds_since_creation(self):
        return (datetime.datetime.utcnow() -
                self.created_at.replace(tzinfo=pytz.utc)).seconds

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
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
                except Exception as exc:
                    pass
            update_fields = changed_fields
        super().save(force_insert, force_update, using, update_fields)


class BaseModel(DateModel, BaseModelUuid):
    class Meta:
        abstract = True