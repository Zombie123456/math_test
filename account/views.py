from rest_framework import mixins, viewsets
from rest_framework.response import Response
from django.utils.translation import ugettext as _

from account.models import Students
from account.serializers import RegisterStudentSerializer
from account.forms import VerificationCodeForm
from mathtest import constants
from mathtest.utils import generate_response
from mathtest.throttling import CustomAnonThrottle


class RegisterStudentViewSet(mixins.CreateModelMixin,
                             viewsets.GenericViewSet):
    model = Students
    permission_classes = []
    queryset = Students.objects.filter()
    serializer_class = RegisterStudentSerializer
    throttle_classes = (CustomAnonThrottle,)

    def create(self, request, *args, **kwargs):
        ret = super(RegisterStudentViewSet, self).create(request)

        if ret.status_code == 201:
            ret.data = {'message': _('Registration successful')}

        return ret


class CaptchaMemberViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    permission_classes = []
    queryset = []

    def list(self, request, *args, **kwargs):
        """
            Request captcha code.
        """

        captcha_form = VerificationCodeForm()
        form_str = str(captcha_form)
        idx = form_str.find('src="')
        src_list = form_str[idx:].split(' ', 1)

        data = {'captcha_src': request.build_absolute_uri(src_list[0][5:-2]),
                'captcha_val': src_list[1].split(' ')[5][7:-1]}

        return generate_response(constants.ALL_OK, data=data)
