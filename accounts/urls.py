from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_user, name='login'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
     path('dashboard/', views.dashboard, name='dashboard'),
     path('create/', views.create_user, name='create_user'),
    path('view/', views.view_users, name='view_users'),
      path('User_edit/<int:pk>/', views.edit_user, name='edit_user'),
      path('user_delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('change-password/', views.change_password, name='change_password'),

    path('export/patient/<int:patient_id>/', views.export_patient_excel, name='export_patient_excel'),
    path('export/doctors/', views.export_doctors_excel, name='export_doctors_excel'),
    path('export/patient/', views.export_patient_selection, name='export_patient_selection'),  # new view
    path('patient/search/', views.patient_search, name='patient_search'),  # AJAX patient search
    path('export/patients/', views.export_all_patients_excel, name='export_all_patients'),
    path('doctor/search/', views.doctor_search, name='doctor_search'),  # AJAX doctor search

    path('backup/', views.backform, name='backup_form'),
    path('restore/', views.restoreform, name='restore_form'),
    path('take-backup/', views.take_backup, name='take_backup'),
    path('restore-backup/', views.restore_backup, name='restore_backup'),
    path('restore-from-upload/', views.restore_from_upload, name='restore_from_upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
