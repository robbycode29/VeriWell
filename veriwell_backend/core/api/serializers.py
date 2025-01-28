from rest_framework import serializers
from core.models import Influencer, Claim

class InfluencerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Influencer
        fields = ['id', 'name', 'profile_picture', 'bio', 'followers', 'trust_score']


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['id', 'influencer', 'claim', 'category', 'date', 'trust_score', 'status', 'evidence', 'counter_evidence']
        depth = 1
