from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check_data_availability/', views.check_data_availability, name='check_data_availability'),
    path('get_data/', views.get_data, name='get_data'),
    path('get_available_data_ranges/', views.get_available_data_ranges, name='get_available_data_ranges'),
]
