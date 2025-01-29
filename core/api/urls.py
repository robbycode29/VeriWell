from rest_framework.routers import DefaultRouter

from core.api.viewsets import InfluencersViewSet, ClaimsViewSet

router = DefaultRouter()
router.register(r'influencers', InfluencersViewSet, basename='influencers')
router.register(r'claims', ClaimsViewSet, basename='claims')
