from django.utils.translation import ugettext as _
from oauth2_provider.models import AccessToken
from rest_framework import permissions
from mathtest.utils import get_user_type


class IsAdmin(permissions.BasePermission):
    message = _('Only authorized users are allowed to access this API')

    def has_permission(self, request, view):
        user = request.user

        return user and user.is_staff


def is_student(user):
    return user and user.groups.filter(name='member_grp').exists() and \
                hasattr(user, 'member_user')


class IsStudent(permissions.BasePermission):
    message = _('Must be atleast a registered student to access API')

    def has_permission(self, request, view):
        user = request.user

        return is_student(user)


def is_staff(user):
    return user and user.groups.filter(name='staff_grp').exists()


class IsStaff(permissions.BasePermission):
    message = _('Only authorized user are allowed to access this API')

    def has_permission(self, request, view):
        user = request.user
        print(user.username)

        return is_staff(user)


def parse_token_param(request):
    token = request.GET.get('token') or ''
    token_obj = AccessToken.objects.filter(token=token).first()

    if token_obj:
        user = token_obj.user
        user_type = get_user_type(user)

        return user, user_type

    return None, None






