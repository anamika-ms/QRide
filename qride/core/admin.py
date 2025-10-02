from django.contrib import admin
from . models import registration, bus, route, ticket,payment
# Register your models here.

admin.site.register(registration)
admin.site.register(bus)
admin.site.register(route)
admin.site.register(ticket)
admin.site.register(payment)