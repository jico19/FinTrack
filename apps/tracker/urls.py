from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard_view'),
    path('history/', views.record_list, name='record_list'),
    path('add-record/', views.add_record, name='add_record'),
    path('edit-record/<int:record_id>/', views.edit_record, name='edit_record'),
    path('delete-record/<int:record_id>/', views.delete_record, name='delete_record'),
    path('update-limit/<int:limit_id>/', views.update_limit, name='update_limit'),
    path('manage-budgets/', views.manage_budgets, name='manage_budgets'),
]
