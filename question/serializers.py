from rest_framework import serializers

from mathtest.utils import parse_request_for_token
from question.models import (Question,
                             StudentTestInfo,
                             StudentQuestion,
                             DateNumber)


class StudentStartTestSerializers(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'title', 'status', 'option', 'points', 'title_img', 'question_type')

    def to_representation(self, instance):
        request = self.context.get('request')
        is_old = self.context.get('old_test')
        if not is_old:
            user, user_type = parse_request_for_token(request)
            s_info = StudentTestInfo.objects.filter(student_id=user.students_user.id).first()
            StudentQuestion.objects.create(start_question=s_info, question=instance)
        ret = super().to_representation(instance)
        return ret


class StudentDateNumberSerializers(serializers.ModelSerializer):
    class Meta:
        model = DateNumber
        fields = '__all__'


class StudentGetTestSerializers(serializers.ModelSerializer):
    class Meta:
        model = StudentQuestion
        fields = ('id', 'student_answer', 'is_correct', 'question')
        depth = 1
