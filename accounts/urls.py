from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
     path('dashboard/', views.dashboard, name='dashboard'),
     path('create/', views.create_user, name='create_user'),
    path('view/', views.view_users, name='view_users'),
      path('user/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('change-password/', views.change_password, name='change_password'),
]
