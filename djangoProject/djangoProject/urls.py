from django.contrib import admin
from django.conf.urls import include, url
from django.urls import path
from page.views import home_view, contact_view, about_view, gallery_view
from django.shortcuts import render
urlpatterns = [
    path('admin/', admin.site.urls),
path('', home_view, name='home'),
path('contact/', contact_view),
url(r'^account/', include('account.urls'))

#path('powitanie/', home_view, name='powitanie')
]
