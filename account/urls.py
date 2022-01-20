from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^/$', views.user_login, name='login')
 ]