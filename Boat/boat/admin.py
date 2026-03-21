from django.contrib import admin

from .models import Case, CurrentState, Keybind, Ship

# Register your models here.
admin.site.register(Ship)
admin.site.register(Case)

admin.site.register(CurrentState)
admin.site.register(Keybind)