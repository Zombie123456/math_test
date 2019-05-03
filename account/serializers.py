import re

from rest_framework import serializers
from django.utils.translation import ugettext as _

from account.models import Students, StudentIds
from django.contrib.auth.models import User, Group
from mathtest.utils import verification_codes


class RegisterStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = '__all__'

    def to_internal_value(self, data):
        request = self.context.get('request')
        code_0 = request.data.get('code_0')
        code_1 = request.data.get('code_1')
        captcha = {'verification_code_0': code_0,
                   'verification_code_1': code_1}
        verified = verification_codes(captcha)
        if verified is False:
            raise serializers.ValidationError(
                {'error': [{'verfification_code_field':
                            _('Incorrect verification code')}]})
        ret = super(RegisterStudentSerializer, self).to_internal_value(data)
        ret['password'] = request.data.get('password')
        ret['copy_password'] = request.data.get('copy_password')
        ret['verification_code_0'] = code_0
        ret['verification_code_1'] = code_1

        return ret

    def validate(self, data):
        validated_data = {}

        # check username
        username = data.get('username')
        user_check = User.objects.filter(username=username)
        id_check = StudentIds.objects.filter(student_id=username).first()
        if user_check or (not id_check):
            raise serializers.ValidationError(
                {'error': [{'username_field': _('username already exists or username error.')}]}
            )
        validated_data['username'] = username
        validated_data['id_obj'] = id_check
        # check password
        password = data.get('password')
        if not password == data.get('copy_password'):
            raise serializers.ValidationError({
                'error': [{'password_field': _('Passwords didn\'t matched')}]
            })
        pattern = re.compile('^[a-zA-Z0-9]{6,15}$')
        if not pattern.match(password):
            msg = _('Password must be 6 to 15 alphanumeric characters')
            raise serializers.ValidationError({
                'error': [{'password_field': _(msg)}]
            })
        validated_data['password'] = password

        return validated_data

    def create(self, validated_data):

        password = validated_data.pop('password')
        id_obj = validated_data.pop('id_obj')
        student = Students.objects.create(**validated_data)
        student.student_id = id_obj
        student.save()
        if student:
            user = User.objects.create_user(
                username=validated_data['username'],
                password=password)

            student_grp = Group.objects.filter(name='student_grp').first()
            user.groups.add(student_grp)

            student.user = user
            student.save()
        return student

