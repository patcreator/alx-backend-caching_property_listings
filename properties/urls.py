from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('metrics/', views.cache_metrics_json, name='cache_metrics'),
    path('report/', views.cache_effectiveness_report, name='cache_report'),
]