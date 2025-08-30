from django.contrib import admin
from . models import registration, bus, route
# Register your models here.

admin.site.register(registration)
admin.site.register(bus)
admin.site.register(route)