from django.core.exceptions import ValidationError
from django.db import models
from django_mysql.models import JSONField

import base64
import json


def is_json(s):
    return isinstance(s, dict) or isinstance(s, list)


def parse(s):
    try:
        return json.loads(s)
    except Exception as e:
        return None


def serialize(s):
    if is_json(s):
        return json.dumps(s, default=str)
    return None


class SimpleJSONField(JSONField):
    def __init__(self, *args, **kwargs):
        super(SimpleJSONField, self).__init__(*args, **kwargs)
    #
    # def from_db_value(self, value, expression, connection, context=None):
    #     if value is None:
    #         return value
    #     return parse(value)
    #
    # def to_python(self, value):
    #     if is_json(value):
    #         return value
    #     if value is None:
    #         return value
    #     return parse(value)
    #
    # def get_prep_value(self, value):
    #     return serialize(value)

