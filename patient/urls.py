from django.urls import path
from . import views

urlpatterns = [
   path('add/', views.add_patient, name='add_patient'),
    path('get-tests/<int:group_id>/', views.get_tests_by_group, name='get_tests_by_group'),
    path('view/', views.view_patients, name='view_patients'),
    path('edit/<int:pk>/', views.edit_patient, name='edit_patient'),
    path('delete/<int:pk>/', views.delete_patient, name='delete_patient'),
    path('receipt/<int:patient_id>/', views.print_receipt, name='print_receipt'),
    path('report/<int:patient_id>/', views.generate_report, name='generate_report'),
    path('print-test-report/<int:patient_id>/', views.print_test_report, name='print_test_report'),

 
   
]
