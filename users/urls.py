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
    path('admin/users/<int:user_id>/', views.change_user_role, name='admin-change-role'),
    path('admin/users/<int:user_id>/toggle-active/', views.toggle_user_active, name='admin-toggle-active'),
    path('admin/users/<int:user_id>/delete/', views.delete_user, name='admin-delete-user'),

    path('auth/logout/', views.logout, name='logout'),
    path('users/', views.list_users, name='list_users'),
    path('auth/password/reset/', views.request_password_reset, name='request_password_reset'),
    path('auth/password/reset/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
    
    path('users/', views.list_users, name='list-users'),
]