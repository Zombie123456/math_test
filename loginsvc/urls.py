from django.conf.urls import url
from loginsvc import views as loginsvc

urlpatterns = [
    url(r'^dashboard_login/', loginsvc.login, name='dashboard_login'),
    url(r'^student_login/', loginsvc.login, name='student_login'),
    url(r'^my/', loginsvc.current_user, name='get_user_and_user_type'),
    url(r'^reset_password/', loginsvc.reset_password, name='reset_password'),
    url(r'^logout/', loginsvc.logout, name='logout'),
    url(r'^refresh_access_token', loginsvc.refresh_access_token, name='refresh_access_token')
]
