from collections import UserDict
from typing import Any

from woocommerce import API
from django.conf import settings
WC_API_KEY = getattr(settings, "WC_API_KEY", 'ck_3f5643c456986d08c1936d93620966da1a43a073')
WC_API_SECRET = getattr(settings, "WC_API_SECRET", 'cs_5fdfff1455be35f5a1916b13fa934abda6bb74c5')
WC_API_URL = getattr(settings, "WC_API_URL", 'http://ec2-34-220-52-244.us-west-2.compute.amazonaws.com/')
WC_API_VERSION = getattr(settings, "WC_API_VERSION", "wc/v3")
WC_API_URL = 'http://staging.deviare.co.za/'

WC_API_KEY = 'ck_9a25ad15d221b5a0786544c6ba334c91e194e2e0'
WC_API_SECRET = 'cs_1f4e054089e938cd7c69b7af5a4d31d91eb6573c'
END_POINTS = dict(
    courses='products',
    categories='products/categories',
    webhooks='webhooks',
    orders='orders'
)


class CRUD(object):
    def __init__(self, api, endpoint):
        self.api = api
        self.endpoint = END_POINTS.get(endpoint, endpoint)
        self.request = None
        self.get_request = None
        self.pages = {}

    def create(self, data):
        self.request = self.api.post(self.endpoint, data)
        return self.request.json()

    def read(self, pk='', params=None):
        kw = {}
        if params is not None:
            kw['params'] = params
        self.get_request = self.api.get('/'.join([self.endpoint, pk]), **kw)
        self.request = self.get_request
        return self.get_request.json()

    def update(self, pk, data):
        self.request = self.api.put('/'.join([self.endpoint, pk]), data)
        return self.request.json()

    def delete(self, pk):
        self.request = self.api.delete('/'.join([self.endpoint, pk]), params={"force": True})
        return self.request.json()

    get = read
    post = create
    put = update
    patch = put


class WcApi(object):
    def __init__(self):
        self._wcapi = API(
            url=WC_API_URL,
            consumer_key=WC_API_KEY,
            consumer_secret=WC_API_SECRET,
            version=WC_API_VERSION
        )
        self._crud = {k: CRUD(self._wcapi, v) for k, v in END_POINTS.items()}

    def _get_create_crud(self, name):
        if name not in self._crud.keys():
            self._crud[name] = CRUD(self._wcapi, name)
        return self._crud[name]

    def __getattribute__(self, name):
        if not str(name).startswith('_'):
            # cr = self._crud.get(name, None)
            # if cr is None:
            #     cr = CRUD(self._wcapi, name)
            #     self._crud[name] = cr
            return self._get_create_crud(name)
        return super().__getattribute__(name)
