from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from redteamcnadmin.views import AuditLogViewSet, NotificationViewSet, TokenSetViewSet, MembershipViewSet, ReviewViewSet, KpiEventViewSet
from django.http import HttpResponse

router = DefaultRouter()
router.register(r'audit', AuditLogViewSet, basename='audit')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'tokensets', TokenSetViewSet, basename='tokenset')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'kpi', KpiEventViewSet, basename='kpi')

def home_view(request):
    return HttpResponse("Bienvenue sur l'API RedTeamCN. Utilisez /api/ pour les endpoints.")

urlpatterns = [
    path('', home_view),
    path('admin/', admin.site.urls),
    path('api/<uuid:org_id>/', include(router.urls)),
    #path('api/auth/', include('dj_rest_auth.urls')),
    #path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
]