from rest_framework.routers import DefaultRouter

from core.api.viewsets import InfluencersViewSet, ClaimsViewSet, BulkResearchViewSet, SingleResearchViewSet, ClaimResearchViewSet

router = DefaultRouter()
router.register(r'influencers', InfluencersViewSet, basename='influencers')
router.register(r'claims', ClaimsViewSet, basename='claims')
router.register(r'bulk_researches', BulkResearchViewSet, basename='bulk_researches')
router.register(r'single_researches', SingleResearchViewSet, basename='single_researches')
router.register(r'claim_researches', ClaimResearchViewSet, basename='claim_researches')
