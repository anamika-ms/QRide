
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
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
