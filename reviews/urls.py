from django.urls import path
from . import views

urlpatterns = [
    path('components/<int:component_id>/reviews/', views.review_list_create, name='review_list_create'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
]