from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# ❌ Supprimer cette ligne
# from redteamcnadmin.views import AuditLogViewSet, NotificationViewSet, TokenSetViewSet, MembershipViewSet, ReviewViewSet, KpiEventViewSet

# ❌ Supprimer tout le bloc de router :
# from rest_framework.routers import DefaultRouter
# router = DefaultRouter()
# router.register(r'audit', AuditLogViewSet, basename='audit')
# router.register(r'notifications', NotificationViewSet, basename='notification')
# router.register(r'tokensets', TokenSetViewSet, basename='tokenset')
# router.register(r'memberships', MembershipViewSet, basename='membership')
# router.register(r'reviews', ReviewViewSet, basename='review')
# router.register(r'kpi', KpiEventViewSet, basename='kpi')

def home_view(request):
    return HttpResponse("Bienvenue sur l'API RedTeamCN. Utilisez /api/ pour les endpoints.")

urlpatterns = [
    path('', home_view),
    path('admin/', admin.site.urls),

    # ❌ Et ici aussi :
    # path('api/<uuid:org_id>/', include(router.urls)),

    # ✅ À la place, ajoute ton app users :
    path('api/users/', include('users.urls')),
]
