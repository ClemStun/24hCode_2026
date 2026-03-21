from django.contrib import admin

from .models import Case, Ship

# Register your models here.
admin.site.register(Ship)
admin.site.register(Case)