from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from page.views import *
from account.views import user_login
from django.shortcuts import render
urlpatterns = [
    path('admin/', admin.site.urls),
path('', home_view, name='home'),
path('contact/', contact_view),
url('login/', user_login),
url('logout/', logout_view),
url('grupy/', group_view)

#path('powitanie/', home_view, name='powitanie')
]
