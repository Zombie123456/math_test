from django.contrib import admin
from account.models import Students, StaffAdmin, StaffPermission, StudentIds


class StudentsAdmin(admin.ModelAdmin):
    list_display = ('username',)


class StaffAdminAdmin(admin.ModelAdmin):
    list_display = ('username',)


class StaffPermissionAdmin(admin.ModelAdmin):
    list_display = ('display_name',)


class StudentIdsAdmin(admin.ModelAdmin):
    list_display = ('student_id',)


admin.site.register(StaffAdmin, StaffAdminAdmin)
admin.site.register(Students, StudentsAdmin)
admin.site.register(StaffPermission, StaffPermissionAdmin)
admin.site.register(StudentIds, StudentIdsAdmin)
