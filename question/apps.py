from __future__ import unicode_literals

from django.apps import AppConfig


class QuestionConfig(AppConfig):
    name = 'question'

    def ready(self):
        import question.signals
