from django.conf.urls import url, include
from rest_framework import routers
from question import views as question


manage_router = routers.DefaultRouter()
student_router = routers.DefaultRouter()

student_router.register(r'start_test', question.StudentStartTestViewSet,
                        base_name='start_test')
student_router.register(r'open_test', question.StudentDateNumberViewSet,
                        base_name='open_test')
student_router.register(r'end_test', question.StudentEndTestViewSet,
                        base_name='end_test')
student_router.register(r'test_info', question.StudentGetPointViewSet,
                        base_name='test_info')

urlpatterns = [
    url(r'^manage/', include(manage_router.urls)),
    url(r'^student/', include(student_router.urls))
]
