from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_notifications, name='list_notifications'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('unread/count/', views.unread_count, name='unread_count'),
]