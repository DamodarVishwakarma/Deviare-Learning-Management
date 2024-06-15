from rest_framework import status as S
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _


def response_data(status, message, data=None):
    if status:
        return {"status": status, "message": _(message), "data": data}
    else:
        return {"status": status, "message": _(message), }


class ResponseWrapper(Response):

    def __init__(
            self,
            data=None,
            status=None,
            template_name=None,
            headers=None,
            exception=False,
            content_type=None,
            **kw):
        status = status if status is not None else S.HTTP_200_OK if data is not None else S.HTTP_400_BAD_REQUEST
        ndata = response_data(
            kw.get('success', S.HTTP_200_OK <= status < S.HTTP_400_BAD_REQUEST),
            kw.get('msg', 'Data Fetched' if status < S.HTTP_400_BAD_REQUEST else 'Something went wrong!!'),
            data
        )
        super().__init__(ndata, status, template_name, headers, exception, content_type)


class RSVPFunc(ResponseWrapper):
    def __init__(self, func=None, *args, **kwargs):
        self.func = None

        if func is not None:
            if callable(func):
                self.func = func
            elif type(func) in (bytes, bytearray, str):
                kwargs['msg'] = kwargs.get('msg', func)
            else:
                kwargs['data'] = kwargs.get('data', func)
        super().__init__(*args, **kwargs)

    def _start(self):
        if self.func:
            if callable(self.func):
                self.func()

    def close(self):
        super().close()
        self._start()

