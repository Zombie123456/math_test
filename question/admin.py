from django.contrib import admin
from question.models import StudentQuestion, Question, StudentTestInfo, DateNumber


class StudentQuestionAdmin(admin.ModelAdmin):
    list_display = ('id',)


class QuestionAdmin(admin.ModelAdmin):
    list_dispay = ('id',)


class StudentTestInfoAdmin(admin.ModelAdmin):
    list_display = ('id',)


class DateNumberAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


admin.site.register(StudentQuestion, StudentQuestionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(StudentTestInfo, StudentTestInfoAdmin)
admin.site.register(DateNumber, DateNumberAdmin)
