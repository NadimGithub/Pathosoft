from django.urls import path
from . import views

urlpatterns = [
    path('', views.ledger_home, name='ledger_home'),
     path('', views.view_ledger, name='view_ledger'),
    path('add/', views.add_ledger, name='add_ledger'),
    path('view/', views.view_ledger, name='view_ledger'),
    path('update/<int:pk>/', views.update_ledger, name='update_ledger'),
    path('delete/<int:pk>/', views.delete_ledger, name='delete_ledger'),
]
