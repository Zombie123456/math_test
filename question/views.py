from rest_framework import mixins, viewsets
from rest_framework.response import Response
from django_filters.utils import timezone
from itertools import chain

from mathtest.throttling import CustomAnonThrottle
from question.models import (Question,
                             StudentTestInfo,
                             StudentQuestion,
                             DateNumber)
from loginsvc.permissions import IsStudent
from question.serializers import (StudentStartTestSerializers,
                                  StudentDateNumberSerializers,
                                  StudentGetTestSerializers)
from mathtest import constants

C_NUMBER = 30
F_NUMBER = 30
B_NUMBER = 30


class StudentStartTestViewSet(mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    model = Question
    permission_classes = [IsStudent]
    serializer_class = StudentStartTestSerializers

    def get_queryset(self):
        queryset_choose_0 = Question.objects.filter(status=1, question_type=0, level=1).\
                              order_by('?').reverse()[:C_NUMBER - int(C_NUMBER * 0.2)]
        queryset_choose_1 = Question.objects.filter(status=1, question_type=0, level=2).\
                                order_by('?').reverse()[:int(C_NUMBER * 0.2)]

        queryset_fill_0 = Question.objects.filter(status=1, question_type=1, level=1).\
                              order_by('?').reverse()[:F_NUMBER - int(F_NUMBER * 0.2)]
        queryset_fill_1 = Question.objects.filter(status=1, question_type=1, level=2).\
                              order_by('?').reverse()[:int(F_NUMBER * 0.2)]

        queryset_big_0 = Question.objects.filter(status=1, question_type=2, level=1).\
                             order_by('?').reverse()[:B_NUMBER - int(B_NUMBER * 0.2)]
        queryset_big_1 = Question.objects.filter(status=1, question_type=2, level=2).\
                             order_by('?').reverse()[:int(B_NUMBER * 0.2)]
        return chain(queryset_big_0, queryset_big_1, queryset_choose_0,
                     queryset_choose_1, queryset_fill_0, queryset_fill_1)

    def list(self, request, *args, **kwargs):
        date_code = self.request.GET.get('datenumber', '')
        date_num = DateNumber.objects.filter(code=date_code, status=1).first()
        if not date_num:
            return Response(data={
                'msg': 'no test now',
                'code': constants.NOT_OK
            }, status=404)
        user = self.request.user
        s_info = StudentTestInfo.objects.filter(student_id=user.students_user.id, date_number=date_num).first()
        chose_list = []
        fill_list = []
        big_list = []
        if s_info:
            query = s_info.stu_que.filter().order_by('id')
            old_test = True
        else:
            old_test = False
            s_info = StudentTestInfo.objects.create(student_id=user.students_user.id, date_number=date_num)
            query = self.get_queryset()
        s_info.date_number = date_num
        s_info.save()
        for info in query:
            try:
                question = info.question
            except:
                question = info
            serializer = StudentStartTestSerializers(question, context={'request': request,
                                                                        'old_test': old_test})
            if serializer.data.get('question_type') == 0:
                chose_list.append(serializer.data)
            elif serializer.data.get('question_type') == 1:
                fill_list.append(serializer.data)
            else:
                big_list.append(serializer.data)
        data = {
            'test_info': {
                'start_question': s_info.id,
                'start_time': s_info.start_time
            },
            'date_ifo': {
                'date_name': date_num.name,
                'all_time': date_num.time,
                'date_code': date_num.code
            },
            'question': {
                'chose_list': chose_list,
                'fill_list': fill_list,
                'big_list': big_list}
        }

        return Response(data, status=200)


class StudentDateNumberViewSet(mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    model = DateNumber
    permission_classes = [IsStudent]
    serializer_class = StudentDateNumberSerializers
    queryset = DateNumber.objects.filter(status=1).order_by('id')


class StudentEndTestViewSet(mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    permission_classes = [IsStudent]

    def create(self, request, *args, **kwargs):
        start_question_id = request.data.get('start_question', '')

        stu_info = StudentTestInfo.objects.filter(id=start_question_id, status=1).first()
        if not stu_info:
            return Response({'error': 'Already submitted',
                             'code': constants.NOT_OK})
        questions = request.data.get('questions', '')

        info_que = StudentQuestion.objects.filter(start_question_id=start_question_id)
        for question in questions:
            question_id = question.get('id')
            student_answer = question.get('student_answer')
            qes_obj = Question.objects.filter(id=question_id).first()
            is_correct = 1
            if qes_obj.answer == student_answer:
                is_correct = 0
            stu_que = info_que.filter(question_id=question_id).first()
            stu_que.student_answer = student_answer
            stu_que.is_correct = is_correct
            stu_que.save()
        stu_info.end_time = timezone.now()
        stu_info.status = 0
        stu_info.save()
        return Response({'msg': 'ok',
                         'code': constants.ALL_OK})


class StudentGetPointViewSet(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    model = StudentQuestion
    permission_classes = [IsStudent]
    serializer_class = StudentGetTestSerializers

    def get_queryset(self):
        user = self.request.user
        date_code = self.request.GET.get('datenumber', '')
        date_num = DateNumber.objects.filter(code=date_code).first()
        if not date_num:
            return Response(data={'error': 'field error',
                                  'code': constants.NOT_OK
                                  }, status=404)

        return date_num.stu_date_num.filter(status=0, student=user.students_user).first().stu_que.filter()

