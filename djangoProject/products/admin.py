from django.contrib import admin

# Register your models here.
from .models import Product
#Dodawanie nowego modelu
admin.site.register(Product)
