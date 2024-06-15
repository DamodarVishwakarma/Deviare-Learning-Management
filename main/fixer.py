from main.models import User, UserSettings, CourseLicenseUser
from main.tasks import *
from main.utils import randomString
import re

REGEX_USERNAME_CHECK = re.compile(r'([A-Z\s]+)')


def valid_username(s):
    return len(REGEX_USERNAME_CHECK.findall(s)) == 0


def create_keyadmin():
    from keycloak import keycloak_admin
    from deviare import settings as deviare_settings
    return keycloak_admin.KeycloakAdmin(
            server_url=deviare_settings.KEYCLOAK_URL,
            username=deviare_settings.KEYCLOAK_ADMINUSER,
            password=deviare_settings.KEYCLOAK_ADMINPASSWORD,
            realm_name=deviare_settings.KEYCLOAK_REALM,
        )


def create_keycloak_user(username=None, email='', password=None, keyadmin=None, **kw):
    if username is None:
        username = email
    if password is None:
        password = randomString()
    if keyadmin is None:
        keyadmin = create_keyadmin()
    try:
        kw.update({
                "email": email,
                "enabled": True,
                "username": username,
                "credentials": [{"value": password, "type": "password"}],
                "realmRoles": ["user_default"],
            })
        keyadmin.create_user(kw)
        return kw
    except Exception as e:
        print(e)
        raise e
    return False


def update_keycloak_user(username=None, email='', old_email=None, keyadmin=None, **kwargs):
    if username is None:
        username =  email
    if keyadmin is None:
        keyadmin = create_keyadmin()
    user = False
    try:
        # search = di
        results = keyadmin.get_users(dict(search=email if old_email is None else old_email))
        user = results[0]
    except Exception as e:
        print(e)
    if user is not False:
        user_id = user['id']
        try:

            keyadmin.update_user(user_id, dict(username=email, email=email))
            return dict(username=email, email=email, user_id=user_id, old_email=old_email)
        except Exception as e:
            print(e)
    return False


def find_keycloak_user(username=None, email='', keyadmin=None, **kwargs):
    
    if username is None:
        username = email
    if keyadmin is None:
        keyadmin = create_keyadmin()
    user = False
    try: 
        results = keyadmin.get_users(dict(search=email))
        user = results[0]
    except Exception as e:
        print(e)
    return user


def delete_keycloak_user(username=None, email='', keyadmin=None, **kwargs):
    if username is None:
        username = email
    if keyadmin is None:
        keyadmin = create_keyadmin()
    user = find_keycloak_user(email=email)
    if user is not False:
        user_id = user['id']
        try:
            keyadmin.delete_user(user_id)
            return user_id
        except Exception as e:
            print(e)
    return False


def fix_keycloak_user(u):
    delete_keycloak_user(email=u.email)
    user = create_keycloak_user(email=u.email)
    u.set_password(user.get('password'))
    usr = u.settings.first()
    usr.set_password(user.get('password'))
    usr.save()
    u.save()
    return user


def find_fix(email=None, password=None):
    if email is None:
        return
    else:
        em = email
    user = User.objects.filter(email__icontains=em)
    user_setting = UserSettings.objects.filter(email__icontains=em)
    keycl= find_keycloak_user(email=em.lower())

    if not user.exists():
        print('No user')
        return user_setting, keycl
    else:
        user = user.first()
        user_setting = user_setting.first()
    email =  str(em).lower().replace(' ', '')
    user.email = email
    user.username = email
    user_setting.userName = email
    user_setting.email = email
    user.save()
    user_setting.save()
    if keycl['username'] != email:
        if password is None:
            return fix_keycloak_user(user)
        else:
            ka = create_keyadmin()
            ka.delete_user(keycl['id'])
            create_keycloak_user(username=email, email=email, password=password)


def create_or_update(instance=None, password=None, keyadmin=None):
    if instance is None:
        return
    if keyadmin is None:
        keyadmin = create_keyadmin()

    user_val = find_keycloak_user(email=instance.email)
    if user_val:
        keyadmin.update_user(
            user_id=user_val.get('id'),
            payload={
                "email": instance.email,
                "username": instance.userName,
                "enabled": True,
                "firstName": instance.lastName,
                "lastName": instance.lastName,
            },
        )
    else:
        if password is None:
            password = randomString()
            instance.set_password(password)
            user = instance.user
            user.set_password(password)
            instance.save()
            user.save()

        keyadmin.create_user(
            {
                "email": instance.email,
                "username": instance.userName,
                "enabled": True,
                "firstName": instance.firstName,
                "lastName": instance.lastName,
                "credentials": [{"value": password, "type": "password"}],
            }
        )

