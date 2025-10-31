from django.urls import path
from . import views

urlpatterns = [
    path('', views.lab_list, name='lab_list'),
    path('add/', views.lab_create, name='lab_create'),
    path('edit/<int:pk>/', views.lab_update, name='lab_update'),
    path('delete/<int:pk>/', views.lab_delete, name='lab_delete'),


]
