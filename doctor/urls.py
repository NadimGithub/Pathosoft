from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_doctor, name='add_doctor'),
    path('view/', views.view_doctors, name='view_doctors'),
    path('update/<int:pk>/', views.update_doctor, name='update_doctor'),
    path('delete/<int:pk>/', views.delete_doctor, name='delete_doctor'),
    path('commission/', views.doctor_commission, name='doctor_commission'),
    # path('search-doctors/', views.search_Doctors, name='search_Doctors'),

]   
