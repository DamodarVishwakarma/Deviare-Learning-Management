from functools import wraps
from django.utils.decorators import method_decorator
from tools.responders import ResponseWrapper, RSVPFunc, Response
from django.http import FileResponse
from django.shortcuts import HttpResponse
from main.models import UserSettings
import traceback


def limit_params(use_params=('username', 'email', 'password'), **kwargs_main):
    def decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            kw = {k: v for k, v in kwargs.items() if k in use_params}
            return func(*args, **kw)
        return wrapped_func
    return decorator


def base_data_response(**kwargs):
    def _response_controller(viewfunc):
        @wraps(viewfunc)
        def _response_controlled(request, *args, **kw):
            kw.update(request.data)
            kw.update(request.query_params)
            if request.user and request.user.is_authenticated:
                request.userAuth = UserSettings.objects.filter(userName=request.user.username).first()
            else:
                print(f"USER: {str(request.user)}")
            try:
                response = viewfunc(request, *args, **kw)
                if isinstance(response, dict):
                    if 'func' in response:
                        fn = response.pop('func')
                        print('func')
                        return RSVPFunc(fn, **response)
                    elif 'success' in response and ('msg' in response or 'data' in response):
                        return ResponseWrapper(**response)
                elif isinstance(response, Response) or isinstance(response, HttpResponse) or isinstance(response, FileResponse):
                    return response
                elif isinstance(response, tuple) or isinstance(response, list):
                    return ResponseWrapper(*response)
                return ResponseWrapper(response)
            except Exception as e:
                traceback.print_stack()
                traceback.print_exc()
                if hasattr(e, 'as_response'):
                    return e.as_response()
                return ResponseWrapper(success=False, msg=f'Something has gone wrong!! || {str(e)}', status=400)
        return _response_controlled
    return _response_controller


data_response = method_decorator(base_data_response())
