from django.urls import path
from . import views

app_name = 'ecourt'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/get-states/', views.get_states, name='get_states'),
    path('api/get-districts/', views.get_districts, name='get_districts'),
    path('api/get-complexes/', views.get_court_complexes, name='get_complexes'),
    path('api/get-courts/', views.get_courts, name='get_courts'),
    path('api/download-cause-list/', views.download_cause_list, name='download_cause_list'),
]