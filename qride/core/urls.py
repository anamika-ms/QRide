
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
    path('routes/', views.view_routes, name='view_routes'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
