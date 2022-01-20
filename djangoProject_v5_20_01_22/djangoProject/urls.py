from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from page.views import *
from account.views import user_login
from django.shortcuts import render, redirect

urlpatterns = [
    path('admin/', admin.site.urls),
path('', home_view, name='home'),
url('login/', user_login),
url('logout/', logout_view),
url('grupy/', group_view, name='grupy'),
url(r'^details/grupa/(?P<id>[0-9]+)$', detail_group_view, name='detail_group_view'),
url('zawodnicy/', competitor_view),
# url(r'^trenerzy/', coach_view, name='trenerzy'),
url(r'^trenerzy/', coach_view, name='trenerzy_szukani'),
url('plany/', plan_view),
url('diety/', diet_view),
url('dyscypliny/', discipline_view),
url('profil/', profile_view),
url('typydyscyplin/', typedisc_view),
url(r'^usuniete/(?P<id>[0-9]+),(?P<typ>[a-zA-Z]+)$', usuwanie, name='usun'),
url(r'^detailspla/plan/(?P<id>[0-9]+)$', detail_plan_view, name='detail_plan_view'),
url(r'^detailstre/trener/(?P<id>[0-9]+)$', detail_coach_view, name='detail_coach_view'),
url(r'^detailszaw/zawodnik/(?P<id>[0-9]+)$', detail_competitor_view, name='detail_competitor_view'),


#path('powitanie/', home_view, name='powitanie')
]
