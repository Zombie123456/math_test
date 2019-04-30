from django.db import models
from django.contrib.auth.models import User


STATUS_OPTIONS = (
    (0, 'Inactive'),
    (1, 'Active')
)


class StudentIds(models.Model):
    student_id = models.CharField(unique=True, max_length=100)


class Students(models.Model):
    '''
    @class Students
    student database
    '''

    user = models.OneToOneField(User, null=True,
                                blank=True, related_name='students_user',
                                on_delete=models.SET_NULL)
    username = models.CharField(unique=True, max_length=100)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True,
                                   blank=True, related_name='students_updated_by',
                                   on_delete=models.SET_NULL)
    is_logged_in = models.BooleanField(default=False)
    last_logged_in = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)

    def __str__(self):
        return self.username


class StaffPermission(models.Model):
    '''
    @class StaffPermission
    '''

    display_name = models.CharField(max_length=50, null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    key = models.CharField(max_length=50, null=False, blank=False, unique=True)

    def __str__(self):
        return self.display_name


class StaffAdmin(models.Model):
    '''
    @class Staff
    staff database
    ForeignKey: User, StaffPermission
    '''

    user = models.OneToOneField(User, null=True,
                                blank=True, related_name='staff_user',
                                on_delete=models.SET_NULL)
    username = models.CharField(unique=True, max_length=100)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=70, blank=True, null=True)
    memo = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, null=True,
                                   blank=True, related_name='staff_created_by',
                                   on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, null=True,
                                   blank=True, related_name='staff_updated_by',
                                   on_delete=models.SET_NULL)
    is_logged_in = models.BooleanField(default=False)
    last_logged_in = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(default=1, choices=STATUS_OPTIONS)
    perms = models.ManyToManyField(StaffPermission,
                                   related_name='staffperms')

    def __str__(self):
        return self.username
