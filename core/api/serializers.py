from rest_framework import serializers
from core.models import Influencer, Claim, BulkResearch, SingleResearch, ClaimResearch

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = ['id', 'name', 'category', 'profile_picture', 'bio', 'followers', 'trust_score']


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'influencer', 'claim', 'category', 'date', 'trust_score', 'status', 'evidence', 'counter_evidence']
        depth = 1


class BulkResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkResearch
        fields = ['id', 'influencers', 'created_at', 'updated_at']
        depth = 1


class SingleResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleResearch
        fields = ['id', 'influencer', 'created_at', 'updated_at']
        depth = 1


class ClaimResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimResearch
        fields = ['id', 'claim', 'created_at', 'updated_at']
        depth = 2


