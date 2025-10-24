from django.urls import path
from . import views

urlpatterns = [
    path('components/', views.list_components, name='list_components'),
    path('components/create/', views.create_component, name='create_component'),
]