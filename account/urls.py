from django.conf.urls import url, include
from rest_framework import routers
from account import views as account


manage_router = routers.DefaultRouter()
student_router = routers.DefaultRouter()

student_router.register(r'register', account.RegisterStudentViewSet,
                        base_name='register')
student_router.register(r'getcode_img', account.CaptchaMemberViewSet,
                        base_name='getcode_img')
urlpatterns = [
    url(r'^manage/', include(manage_router.urls)),
    url(r'^student/', include(student_router.urls))
]
