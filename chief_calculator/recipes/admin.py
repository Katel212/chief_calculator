from django.contrib import admin
from django.contrib.auth.models import User

from .models import Recipe, Ingredient

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Ingredient)
