from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework import response

from core.flows import InfluencerFlow, InfluencersFlow, HealthClaimsFlow


class InfluencersViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def new(self, request):
        key = request.query_params.get('key')
        journals = request.query_params.get('journals')
        comment = request.query_params.get('comment')

        # retrieve new influencers
        flow = InfluencersFlow(key)
        resp = flow.discover_influencers()

        # retrieve health claims
        for influencer in resp:
            health_flow = HealthClaimsFlow(key, influencer, journals, comment)
            health_resp = health_flow.discover_health_claims()
            influencer['health_claims'] = health_resp
            ## overall trust score of influencer (avg)
            influencer['trust_score'] = sum([claim['trust_score'] for claim in health_resp]) / len(health_resp)

        return response.Response(data=resp)

    @action(detail=False, methods=['get'])
    def check_influencer(self, request):
        key = request.query_params.get('key')
        influencer = request.query_params.get('influencer')
        max_claims = request.query_params.get('max_claims')
        min_claims = request.query_params.get('min_claims')

        # retrieve influencer
        flow = InfluencerFlow(key, influencer)
        resp = flow.check_influencer()

        # retrieve health claims
        health_flow = HealthClaimsFlow(key, influencer, max_claims=max_claims, min_claims=min_claims)
        health_resp = health_flow.discover_health_claims()
        resp['health_claims'] = health_resp
        ## overall trust score of influencer (avg)
        resp['trust_score'] = sum([claim['trust_score'] for claim in health_resp]) / len(health_resp)

        return response.Response(data=resp)

