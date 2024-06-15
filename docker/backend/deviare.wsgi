import os
import sys
import site

prev_sys_path = list(sys.path)
site.addsitedir('/usr/local/lib/python3.7/dist-packages')

sys.path.append('/backend/');

os.environ['DJANGO_SETTINGS_MODULE'] = 'deviare.settings'


sys.path.extend([
   '/usr/local/lib/python3.7/dist-packages',
   '/usr/local/lib/python3.7/dist-packages/django/contrib/admindocs',
])
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
