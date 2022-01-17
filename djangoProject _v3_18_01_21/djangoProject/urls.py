from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from page.views import *
from account.views import user_login
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
path('', home_view, name='home'),
url('login/', user_login),
url('logout/', logout_view),
url('grupy/', group_view),
url('details_group/', detail_group_view, name='detail_group_view')


#path('powitanie/', home_view, name='powitanie')
]
