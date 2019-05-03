# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import localtime

from question.models import StudentTestInfo
from .tasks import deal_overdue


logger = logging.getLogger(__name__)


@receiver(post_save, sender=StudentTestInfo, dispatch_uid='transaction_follow_up')
def transaction_follow_up(sender, instance, created, **kwargs):
    """
    """
    if created:
        expired_in_minutes = 120
        date_time = instance.date_number

        if date_time:
            expired_in_minutes = date_time.time
        deal_overdue.apply_async((instance.id,),
                                 eta=localtime() + timedelta(minutes=expired_in_minutes))
