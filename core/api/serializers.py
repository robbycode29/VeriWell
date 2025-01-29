from rest_framework import serializers
from core.models import Influencer, Claim, BulkResearch, SingleResearch, ClaimResearch

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = ['id', 'name', 'category', 'profile_picture', 'bio', 'followers', 'trust_score', 'verified_claims']

    verified_claims = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()

    def get_verified_claims(self, obj):
        return obj.claims.count()

    def get_followers(self, obj):
        ## e.g. Follower count will be displayed as 2M+ instead of 2000000 for better readability
        if obj.followers is None:
            return "0"
        if obj.followers >= 1000000:
            return str(obj.followers // 1000000) + "M+"
        elif obj.followers >= 1000:
            return str(obj.followers // 1000) + "K+"
        else:
            return obj.followers


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'influencer', 'claim', 'category', 'date', 'trust_score', 'status', 'evidence', 'counter_evidence']
        depth = 1


class BulkResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkResearch
        fields = ['id', 'influencers', 'failed', 'created_at', 'updated_at']
        depth = 1


class SingleResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleResearch
        fields = ['id', 'influencer', 'failed', 'created_at', 'updated_at']
        depth = 1


class ClaimResearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimResearch
        fields = ['id', 'claim', 'failed', 'created_at', 'updated_at']
        depth = 2


