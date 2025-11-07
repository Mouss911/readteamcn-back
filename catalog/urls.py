from django.urls import path
from . import views

urlpatterns = [
    path('components/', views.list_components, name='list_components'),
    path('components/create/', views.create_component, name='create_component'),
    path('components/<int:pk>/', views.update_component, name='update_component'),
    path('components/<int:pk>/', views.delete_component, name='delete_component'),
    path('components/submit/<int:component_id>/', views.submit_for_review, name='submit_for_review'),
    path('components/review/<int:component_id>/', views.review_component, name='review_component'),
    path('components/my/', views.my_components, name='my_components'),
    path('coach/stats/', views.coach_dashboard_stats, name='coach-dashboard-stats'),
    path('categories/', views.list_categories, name='list_categories'),
]