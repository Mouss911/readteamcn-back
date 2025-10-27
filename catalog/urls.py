from django.urls import path
from . import views

urlpatterns = [
    path('components/', views.list_components, name='list_components'),
    path('components/create/', views.create_component, name='create_component'),
    path('components/<int:pk>/', views.update_component, name='update_component'),
    path('components/<int:pk>/', views.delete_component, name='delete_component'),
]