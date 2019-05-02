import logging
import string
import hashlib
import random
import re
import requests

from rest_framework.decorators import (api_view,
                                       permission_classes,
                                       throttle_classes)
from rest_framework.response import Response
from django.core.cache import cache
from django.http.request import QueryDict
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.utils.datastructures import MultiValueDictKeyError
from django.urls import resolve
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_condition import Or

from mathtest.throttling import CustomAnonThrottle
from mathtest.utils import generate_response
from mathtest import constants
from mathtest import settings
from account.models import StaffAdmin, Students
from mathtest.utils import get_user_type, parse_request_for_token, get_valid_token
from loginsvc.permissions import IsStaff, IsStudent


logger = logging.getLogger(__name__)


def set_auth(sessionid, message):
    data = {
        'sessionid': sessionid,
    }
    cache.incr(sessionid)
    response = generate_response(constants.FIELD_ERROR,
                                 msg=message,
                                 data=data)
    response.set_cookie(key='sessionid', value=sessionid)
    return response


def random_token_generator(length):
    seq = string.ascii_lowercase + string.digits
    return ''.join(random.choices(seq, k=length))


def generate_token(string_0, string_1):
    salt = random_token_generator(4)
    token = f'{string_0}.{string_1}.{salt}'
    return hashlib.md5(token.encode('utf-8')).hexdigest()


@api_view(['POST'])
@throttle_classes([CustomAnonThrottle])
@permission_classes([])
@csrf_exempt
def login(request):
    sessionid = request.COOKIES.get('sessionid')

    # create session if cannot find it in cookies or cache
    if not sessionid or cache.get(sessionid) is None:
        try:
            request.session.create()
            sessionid = request.session.session_key
            cache.set(sessionid, 0, 3600)  # 1 hour
        except Exception as e:
            logging.error(str(e))

    data = request.POST or QueryDict(request.body)  # to capture data in IE

    # verify username and password
    try:
        user = authenticate(username=data['username'],
                            password=data['password'])
    except MultiValueDictKeyError:
        return generate_response(constants.NOT_ALLOWED,
                                 _('Not Allowed Login'))

    # get user type (admin, staff, None)
    user_type = get_user_type(user)
    url_name = resolve(request.path).url_name

    # if user login to wrong website or username/password is invalid
    if (url_name == 'dashboard_login' and user_type is not 'staff') or\
            (url_name == 'student_login' and user_type is not 'student'):
        msg = _('Invalid username or password')
        return set_auth(sessionid, msg)

    is_active = __get_status(user, user_type)

    if is_active:
        cache.delete(sessionid)

        token = create_token(user, user_type, url_name.split('_')[0])
        if user_type == 'staff':
            staff = user.staff_user
            staff.is_logged_in = True
            staff.last_logged_in = timezone.now()
            staff.save()
        elif user_type == 'student':
            student = user.students_user
            student.is_logged_in = True
            student.last_logged_in = timezone.now()
            student.save()

        response = generate_response(constants.ALL_OK, data=token)
        response.set_cookie(key='access_token',
                            value=token['access_token'])
        response.set_cookie(key='refresh_token',
                            value=token['refresh_token'])
        response.set_cookie(key='auth_req', value='')

        return response
    else:
        return generate_response(constants.NOT_ALLOWED, _('This account has been suspended'))


def create_token(user, user_type, name):

    expire_seconds = settings.OAUTH2_PROVIDER['ACCESS_TOKEN_EXPIRE_SECONDS']
    scopes = settings.OAUTH2_PROVIDER['SCOPES']

    application = Application.objects.get(name=name)

    AccessToken.objects.filter(user=user, application=application).delete()

    expires = timezone.localtime() + timezone.timedelta(seconds=expire_seconds)

    user_token = generate_token(user.username, user.date_joined.strftime('%Y-%m-%d %H:%M:%S'))

    access_token = AccessToken.objects.create(user=user,
                                              application=application,
                                              token=user_token,
                                              expires=expires,
                                              scope=scopes)

    refresh_token = RefreshToken.objects.create(user=user,
                                                application=application,
                                                token=generate_token(user_token, 'refresh'),
                                                access_token=access_token)

    token = {
        'access_token': access_token.token,
        'token_type': 'Bearer',
        'expires_in': expires.strftime('%Y-%m-%d %H:%M:%S'),
        'refresh_token': refresh_token.token,
        'type': user_type
    }

    return token


def __get_status(user, user_type):
    if user:
        if user_type == 'admin':
            return user.is_active
        elif user_type == 'staff':
            staff = StaffAdmin.objects.filter(username=user).first()
            return staff and staff.status == 1
        else:
            staff = Students.objects.filter(username=user).first()
            return staff and staff.status == 1

    return False


def force_logout(user):
    # Logout immediately
    token_obj = AccessToken.objects.filter(user=user).first()
    try:
        user = token_obj.user
        user_type = get_user_type(user)
        # deleting AccessToken will also delete RefreshToken
        token_obj.delete()
        if user_type == 'staff':
            staff = user.staff_user
            staff.is_logged_in = False
            staff.save()
        return generate_response(constants.ALL_OK)
    except:
        generate_response(constants.NOT_OK, _('Request failed.'))


@csrf_exempt
@api_view(['GET'])
def current_user(request):
    user, user_grp = parse_request_for_token(request)
    if not user:
        return Response(data=constants.NOT_OK, status=404)
    if getattr(user, 'students_user', ''):
        username = user.students_user.student_id.name
    else:
        username = user.username
    return Response({'username': username,
                     'type': get_user_type(user)},
                    status=200)


@csrf_exempt
@api_view(['POST'])
@permission_classes([Or(IsStaff, IsStudent)])
def reset_password(request):
    if request.method == 'POST':
        token_obj = get_valid_token(request)

        if token_obj:
            user_tok = token_obj.user
            username = user_tok.username

            if request.POST:
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')
                repeat_password = request.POST.get('repeat_password')
            else:
                old_password = request.data.get('old_password')
                new_password = request.data.get('new_password')
                repeat_password = request.data.get('repeat_password')

            user = authenticate(username=username, password=old_password)

            if not user:
                return generate_response(constants.FIELD_ERROR,
                                         _('Incorrect previous password'))

            if repeat_password != new_password:
                return generate_response(constants.FIELD_ERROR,
                                         _('Passwords didn\'t matched'))

            pattern = re.compile('^[a-zA-Z0-9]{6,15}$')
            if not pattern.match(new_password):
                msg = _('Password must be 6 to 15 alphanumeric characters')
                return generate_response(constants.FIELD_ERROR, msg)

            user.set_password(new_password)
            user.save()

            force_logout(user)

            return generate_response(constants.ALL_OK)

    return generate_response(constants.NOT_ALLOWED, _('Not Allowed'))


@csrf_exempt
@api_view(['POST'])
def logout(request):
    # if request.method != 'POST':
    #     return generate_response(constants.NOT_ALLOWED, _('Not Allowed'))

    access_token = (request.META.get('HTTP_AUTHORIZATION') or '').split(' ')
    if access_token and len(access_token) == 2 \
            and access_token[0] == 'Bearer':
        access_token = access_token[1]
    else:
        return generate_response(constants.NOT_OK, _('Request failed.'))

    token_obj = AccessToken.objects.filter(token=access_token).first()
    try:
        user = token_obj.user
        user_type = get_user_type(user)
        # deleting AccessToken will also delete RefreshToken
        token_obj.delete()

        if user_type == 'staff':
            staff = user.staff_user
            staff.is_logged_in = False
            staff.save()
        elif user_type == 'student':
            student = user.students_user
            student.is_logged_in = False
            student.save()
        return generate_response(constants.ALL_OK)
    except:
        return generate_response(constants.NOT_OK, _('Request failed.'))


@api_view(['POST'])
@permission_classes([])
@csrf_exempt
def refresh_access_token(request):
    # Refresh the access token
    refresh_token = request.data.get('refresh_token') or \
        request.POST.get('refresh_token')

    refresh_token_obj = \
        RefreshToken.objects.filter(token=refresh_token).first()

    # Check whether if the refresh token exists
    if not refresh_token_obj:
        return generate_response(constants.NOT_OK,
                                 _('Please make sure you are logged in'))

    client_id = refresh_token_obj.application.client_id
    client_secret = refresh_token_obj.application.client_secret
    user_obj = refresh_token_obj.user

    if not user_obj.is_active:
        return generate_response(constants.NOT_ALLOWED,
                                 _('This account has been suspended'))

    url = f'{request.scheme}://{request.get_host()}/o/token/'

    data = {'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token}

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.post(url, data=data, headers=headers)
        tokens = response.json()
        new_access_tk = tokens.get('access_token')
        new_refresh_tk = tokens.get('refresh_token')
    except:
        return generate_response(constants.NOT_OK, _('Refresh failed'))

    if response.status_code == 200 and new_access_tk and new_refresh_tk:
        expires_in = AccessToken.objects.filter(token=new_access_tk).\
            values('expires').first()
        if not expires_in:
            return generate_response(constants.NOT_OK, _('Refresh failed'))

        expires = timezone.localtime(expires_in['expires'])

        new_token = {
            'access_token': new_access_tk,
            'token_type': 'Bearer',
            'expires_in': expires.strftime('%Y-%m-%d %H:%M:%S'),
            'refresh_token': new_refresh_tk,
        }

        response = generate_response(constants.ALL_OK, data=new_token)
        response.set_cookie(key='access_token', value=new_access_tk)
        response.set_cookie(key='refresh_token', value=new_refresh_tk)
        return response

    return generate_response(constants.NOT_OK, _('Refresh failed'))
