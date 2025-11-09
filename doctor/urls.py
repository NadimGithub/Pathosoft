from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_doctor, name='add_doctor'),
    path('view/', views.view_doctors, name='view_doctors'),
    path('update/<int:pk>/', views.update_doctor, name='update_doctor'),
    path('delete/<int:pk>/', views.delete_doctor, name='delete_doctor'),
    path('commission/', views.doctor_commission, name='doctor_commission'),
    # path('search-doctors/', views.search_Doctors, name='search_Doctors'),


    path("doctor-ledger/", views.doctor_ledger_list, name="doctor_ledger_list"),
    path("doctor-ledger/<int:doctor_id>/", views.doctor_ledger_detail, name="doctor_ledger_detail"),
    path("doctor-ledger/<int:doctor_id>/add-transaction/", views.add_transaction, name="add_transaction"),
]   
