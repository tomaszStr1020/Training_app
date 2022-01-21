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
url('dodajgrupe/', add_group_view),
url(r'^edytujgrupe/(?P<id>[0-9]+)$', edit_group_view, name='edit_group_view'),



url('zawodnicy/', competitor_view, name='zawodnicy'),
url(r'^detailszaw/zawodnik/(?P<id>[0-9]+)$', detail_competitor_view, name='detail_competitor_view'),
url('dodajzawodnika/', add_competitor_view),
url(r'^przypiszdysc/zawodnikowi/(?P<id>[0-9]+)$', add_disccomp_view, name='add_disccomp_view'),
url(r'^edytujzawodnika/(?P<id>[0-9]+)$', edit_competitor_view, name='edit_competitor_view'),


url('trenerzy/', coach_view, name='trenerzy'),
url(r'^detailstre/trener/(?P<id>[0-9]+)$', detail_coach_view, name='detail_coach_view'),
url('dodajtrenera/', add_coach_view),
url(r'^przypiszdisc/trenerowi/(?P<id>[0-9]+)$', add_disccoach_view, name='add_disccoach_view'),
url(r'^edytujtrenera/(?P<id>[0-9]+)$', edit_coach_view, name='edit_coach_view'),


url('plany/', plan_view),
url(r'^detailspla/plan/(?P<id>[0-9]+)$', detail_plan_view, name='detail_plan_view'),
url('dodajplan/', add_plan_view),
url(r'^edytujplan/(?P<id>[0-9]+)$', edit_plan_view, name='edit_plan_view'),


url('diety/', diet_view, name='diety'),
url('dodajdiete/', add_diet_view, name='dodawanie_diety'),


url('dyscypliny/', discipline_view),
url('dodajdyscypline/', add_disc_view, name='dodajdyscypline'),

url('typydyscyplin/', typedisc_view),

url('dodajtypdysc/',add_typedisc_view, name='dodajtypdyscypliny'),

url('profil/', profile_view),


url(r'^usuniete/(?P<id>[^.]+),(?P<typ>[^.]+)$', usuwanie, name='usun'),



]
