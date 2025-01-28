from rest_framework.routers import DefaultRouter

from core.api.viewsets import InfluencersViewSet

router = DefaultRouter()
router.register(r'influencers', InfluencersViewSet, basename='influencers')
