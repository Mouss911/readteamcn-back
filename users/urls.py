from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', views.me, name='me'),    
    # Endpoints Admin (Platform Admin uniquement)
    path('admin/users/', views.list_all_users, name='admin-list-users'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='admin-delete-user'),
    path('admin/promote/', views.promote_to_platform_admin, name='admin-promote'),

    path('auth/logout/', views.logout, name='logout'),
    path('users/', views.list_users, name='list_users'),
]