from rest_framework.permissions import BasePermission
from tools.authentication import get_object_from_token


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['GET', 'OPTIONS', 'HEAD']


class CanRegister(BasePermission):
    def has_permission(self, request, view):
        print(f'CanRegister {request.method} on {view}')
        return request.method in ['POST', 'OPTIONS', 'HEAD']


class IsLoggedIn(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        print(f'Perm on {view}')
        auth = bool(request.user and request.user.is_authenticated)
        if auth:
            return auth
        data = get_object_from_token(request)
        return bool(data.get('object', False))