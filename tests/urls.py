from django.urls import path
from . import views

urlpatterns = [
    # Test Group URLs
    path('groups/add/', views.add_test_group, name='add_test_group'),
    path('groups/view/', views.view_test_groups, name='view_test_groups'),
    path('groups/update/<int:pk>/', views.update_test_group, name='update_test_group'),
    path('groups/delete/<int:pk>/', views.delete_test_group, name='delete_test_group'),

    # Test Master URLs
    path('add/', views.add_test, name='add_test'),
    path('view/', views.view_tests, name='view_tests'),
    path('update/<int:pk>/', views.update_test, name='update_test'),
    path('delete/<int:pk>/', views.delete_test, name='delete_test'),

    # Method URLs
    path('methods/', views.method_list, name='method_list'),
    path('methods/add/', views.method_add, name='method_add'),
    path('methods/update/<int:pk>/', views.method_update, name='method_update'),
    path('methods/delete/<int:pk>/', views.method_delete, name='method_delete'),
]
