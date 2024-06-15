from rest_framework_simplejwt.authentication import api_settings, TokenError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication, InvalidToken
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainSerializer, RefreshToken
from django.contrib.auth.backends import ModelBackend,BaseBackend
from rest_framework.utils.serializer_helpers import ReturnDict, OrderedDict
import time

SMAP = {
    'auth.User': 'SuperAdmin',
    'main.UserAuth': 'Admin',
    'main.Employer': 'Employer',
    'main.TalentUser': 'TalentUser',
    'main.User': 'Applicant',
}
ROLE_ID_MAP = {
    '0': 'main.Role',
    '1': 'main.UserAuth',
    '2': 'main.Employer',
    '3': 'main.TalentUser',
    '4': 'main.User',
}
SMAP_REVERSED = {v: k for k, v in SMAP.items()
                 # if k != 'auth.User'
                 }
ROLE_ID_MAP.update(SMAP_REVERSED)


def generate_token(data, role='TalentUser'):
    u = data
    if type(data) in (dict, ReturnDict, OrderedDict):
        cls = get_model_for_role(role)
        u = cls.objects.get(pk=data.get('uuid'))
    return UserToken.for_user(u)


def extract_decode_token(request):

    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False
    messages = []
    raw_token = auth_header.split(" ").pop()
    for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
        try:
            decoded = AuthToken(raw_token)

            return decoded
        except TokenError as e:
            messages.append({'token_class': AuthToken.__name__,
                             'token_type': AuthToken.token_type,
                             'message': e.args[0]})
    print(messages)
    return False


def get_object_from_token(request):
    from django.apps import apps
    decoded = extract_decode_token(request)
    result = {'model': False, 'object': False}
    try:
        app = 'main' if decoded.get('role', False) else 'auth'
        model = apps.get_model(app, decoded.get('role'))
        result['model'] = model
        uuid = decoded.get('uuid', decoded.get('user_id', False))
        return dict(object=model.objects.get(pk=uuid), model=model)
    except Exception as e:
        print(e)
    return result


def auth_user(request, asdict=False):
    if asdict:
        return get_dict_from_token(request).get('object', False)
    return get_object_from_token(request).get('object', False)


def get_dict_from_token(request):
    from django.apps import apps
    decoded = extract_decode_token(request)
    result = {'model': False, 'object': False}
    try:
        app = 'main' if decoded.get('user_role', False) else 'auth'
        model = apps.get_model(app, decoded.get('user_role'))
        result['model'] = model
        uuid = decoded.get('uuid', decoded.get('user_id', False))
        return dict(object=model.objects.filter(pk=uuid).values().first(), model=model)
    except Exception as e:
        print('get_dict_from_token', e)
    return result


def get_model(app_model):
    from django.apps import apps
    try:
        app, model = app_model.split('.')
        return apps.get_model(app, model)
    except Exception as e:
        print(e)
        return None


def get_role_str(model):
    return SMAP.get(model)


def get_cls_name(o):
    c = o.__class__
    return '.'.join([c._meta.app_label, c.__name__])


class UserToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        cn = get_cls_name(user)
        user_role = get_role_str(cn)
        user_id = getattr(user, 'uuid') if cn != 'auth.User' else getattr(user, 'id')
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token['user_id'] = user_id
        token['role'] = user_role
        token['user_role'] = user_role
        token['email'] = user.email or '' if hasattr(user, 'email') else ''
        return token


class TokenObtainPairSerializer(TokenObtainSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    @classmethod
    def get_token(cls, user):
        return UserToken.for_user(user)

    def validate(self, attrs):
        if self.user is None:
            self.user = authenticate(None, **attrs)
        if self.user is None:
            raise AuthenticationFailed(
                self.error_messages['no_active_account'],
                'no_active_account',
            )
        data = {}
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


def get_model_for_role(role):
    try:
        return get_model(ROLE_ID_MAP.get(str(role)))
    except Exception as e:
        print('gmfr', e)
        return


def get_role_models():
    return [get_model_for_role(k) for k in '2,3,4,1'.split(',')]


def get_user_by_elimination(password=None, **kwargs):
    def authen(model):
        try:
            user = model.objects.get(**kwargs)
            return user
        except model.DoesNotExist:
            model().set_password(password)
        return None
    # get user models
    for m in get_role_models():
        u = authen(m)
        if u is not None:
            return u
    return None


def get_username(**kwargs):
    r = 'email' if 'email' in kwargs else 'username' if 'username' in kwargs else False
    if r is False:
        return None, None
    return kwargs.get('email', kwargs.get('username', None)), r


class AuthBackend(BaseBackend):

    def authenticate(self, request,  password=None, **kwargs):
        UserAuth = get_user_model()
        username, ukey = get_username(**kwargs)
        if username is None or password is None:
            return None
        try:
            user = UserAuth.objects.get(**{ukey: username})
        except UserAuth.DoesNotExist:
            UserAuth().set_password(password)
            user = get_user_by_elimination(password=password, **{ukey: username})

        if user is not None:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None

    def user_can_authenticate(self, user):
        return True

    def get_user(self, uuid):
        UserAuth = get_user_model()
        try:
            return UserAuth.objects.get(pk=uuid)
        except UserAuth.DoesNotExist:
            return get_user_by_elimination(None, pk=uuid)


class TokenJWTAuthentication(JWTAuthentication):

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        role = validated_token.get('role', None)
        if role is None:
            raise InvalidToken(_('Token contained no recognizable user identification'))
        model = get_model_for_role(role)
        user_id = validated_token.get('user_id', validated_token.get('uuid', None))
        if user_id is None:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        if int(validated_token.get('exp', '0')) < int(time.time()):
            msg = _('Login Session has expired.')
            raise AuthenticationFailed(msg)
        if model is None:
            model = get_user_model()
        try:
            user = model.objects.get(pk=user_id)
        except model.DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if role.endswith('Admin'):
            if not user.is_active:
                raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


def update_user_pass(email, new_password):
    from main.models import UserAuth
    u = UserAuth.objects.get(email=email)
    u.set_passord(new_password)
    return u


def create_user(email, password, role=2):
    from main.models import UserAuth
    is_super = role in ('Admin', 1)
    return UserAuth.objects.create_superuser(
        email, password, role
    ) if is_super else UserAuth.objects.create_user(
        email, password, role
    )


