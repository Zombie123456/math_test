from django.db import models
from mathtest.utils import PathAndRename
from account.models import Students
from django_filters.utils import timezone


STATUS_OPTIONS = (
    (0, 'Inactive'),
    (1, 'Active')
)

QUESTION_OPTIONS = (
    (1, 'A'),
    (2, 'B'),
    (3, 'C'),
    (4, 'D')
)


QUESTION_TYPE_OPTIONS = (
    (0, 'Choose question'),
    (1, 'Fill question'),
    (2, 'Big question')
)


CORRECT_OPTIONS = (
    (0, 'Correct'),
    (1, 'Error')
)


class DifficultOptions(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)
    key = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Question(models.Model):
    question_type = models.IntegerField(default=0, choices=QUESTION_TYPE_OPTIONS)
    title = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)
    answer = models.TextField(null=True, blank=True)
    option = models.TextField(null=True, blank=True)
    title_img = models.ImageField(upload_to=PathAndRename('question_img'), null=True, blank=True)
    level = models.ForeignKey(DifficultOptions, on_delete=models.PROTECT)
    points = models.IntegerField()

    def __str__(self):
        return self.title[:5]


class DateNumber(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, null=True, blank=True)
    time = models.CharField(max_length=30, null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)


class StudentTestInfo(models.Model):
    student = models.ForeignKey(Students, on_delete=models.PROTECT)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)
    date_number = models.ForeignKey(DateNumber, on_delete=models.PROTECT,
                                    null=True, blank=True, related_name='stu_date_num')


class StudentQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    student_answer = models.TextField(null=True, blank=True)
    is_correct = models.IntegerField(null=True, blank=True, choices=CORRECT_OPTIONS)
    start_question = models.ForeignKey(StudentTestInfo, null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name='stu_que')

