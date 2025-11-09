from django.urls import path
from . import views

urlpatterns = [
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.department_create, name='department_create'),
    path('departments/<int:dept_id>/edit/', views.department_update, name='department_update'),
    path('departments/<int:dept_id>/delete/', views.department_delete, name='department_delete'),

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

    path("add-test-ajax/", views.add_test_ajax, name="add_test_ajax"),
    path('update_test_ajax/<int:test_id>/', views.update_test_ajax, name='update_test_ajax'),
    path('tests/update_test_compulsory/', views.update_test_compulsory, name='update_test_compulsory'),

    path("get-tests/<int:group_id>/", views.get_tests, name="get_tests"),
    path("get-tests/all/", views.get_all_tests, name="get_all_tests"),
]
