import os
from uuid import uuid4

from account.forms import VerificationCodeForm
from django.http import JsonResponse
from django.utils.deconstruct import deconstructible
from oauth2_provider.models import AccessToken


def verification_codes(captcha_dict):
    '''
    Check if the capcha is correct or not
    '''

    verify_form = VerificationCodeForm(captcha_dict)

    return verify_form.is_valid()


def generate_response(code, msg=None, data=None):
    response = {'code': code,
                'msg': msg,
                'data': data}

    return JsonResponse(response, status=200)


def get_user_type(user):
    if user:
        if hasattr(user, 'staff_user'):
            return 'staff'
        elif hasattr(user, 'students_user'):
            return 'student'
        else:
            return 'admin'
    return None


def parse_request_for_token(request):
    token = (request.META.get('HTTP_AUTHORIZATION') or '').split(' ')

    if len(token) < 2 or token[0] != 'Bearer':
        return None, None

    access_token = token[1]
    token_obj = AccessToken.objects.filter(token=access_token). \
        select_related('user').first()

    if not token_obj:
        return None, None

    user = token_obj.user

    if not user:
        return None, None
    user_group = (user.groups.filter(name='staff_grp').first() or
                  user.groups.filter(name='student_grp').first() or None)

    return user, user_group


def get_valid_token(request, try_cookies=False, select_related_user=True):
    # get access token string
    auth_str = request.META.get('HTTP_AUTHORIZATION') or ''
    auth_segments = auth_str.split(' ')
    if len(auth_segments) >= 2 and auth_segments[0] == 'Bearer':
        access_token_str = auth_segments[1]
    elif try_cookies:
        access_token_str = request.COOKIES.get('access_token')
    else:
        return None

    if select_related_user:
        access_token = AccessToken.objects.select_related('user') \
            .filter(token=access_token_str) \
            .first()
    else:
        access_token = AccessToken.objects.filter(token=access_token_str) \
            .first()
    if not access_token or access_token.is_expired():
        return None
    return access_token


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]

        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)

        # return the whole path to the file
        return os.path.join(self.path, filename)
