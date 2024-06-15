
from django.conf import settings

try:
    import json
    SESSION_REDIS_JSON_ENCODING = getattr(settings, 'SESSION_REDIS_JSON_ENCODING', 'utf8')


    class UjsonSerializer(object):
        def dumps(self, obj):
            return json.dumps(obj, default=str).encode(
                SESSION_REDIS_JSON_ENCODING
            )

        def loads(self, data):
            return json.loads(
                data.decode(SESSION_REDIS_JSON_ENCODING)
            )
except ImportError:
    pass