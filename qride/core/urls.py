
from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),

    path('contact/', views.contact, name='contact'),
    path('details/', views.details, name='details'),
    path('listing/', views.listing, name='listing'),

    path('bus_home/', views.bus_home, name='bus_home'),
    path('stu_home/', views.stu_home, name='stu_home'),
    path('pass_home/', views.pass_home, name='pass_home'),

    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    path('add_bus/', views.add_bus, name='add_bus'),
    path('add_route/', views.add_route, name='add_route'),
    path('view_routes/', views.view_routes, name='view_routes'),

    path('select-destination/', views.select_destination, name='select_destination'),
    path('generate-ticket/<int:bus_id>/<int:route_id>/', views.generate_ticket, name='generate_ticket'),
    path('operator-tickets/', views.operator_tickets, name='operator_tickets'),
    path('travel_history/', views.travel_history, name='travel_history'),

    path('view-ticket/<int:ticket_id>/', views.view_ticket, name='view_ticket'),

    path('pay/<int:ticket_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment-success/<int:ticket_id>/', views.payment_success, name='payment_success'),

    path('download-ticket/<int:ticket_id>/', views.download_ticket, name='download_ticket'),
    path('operator/bus-report/<int:bus_id>/', views.operator_bus_report, name='operator_bus_report'),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
