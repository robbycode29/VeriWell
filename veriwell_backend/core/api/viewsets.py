from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework import response

from core.flows import InfluencerFlow, InfluencersFlow, HealthClaimsFlow, SingleClaimFlow
from core.models import BulkResearch, SingleResearch, ClaimResearch, Influencer, Claim, ResearchPaper


class InfluencersViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['post'])
    def check_bulk(self, request):
        key = request.query_params.get('key')
        model = request.query_params.get('model', 'sonar')
        journals = request.query_params.get('journals')
        comment = request.query_params.get('comment')
        count = request.query_params.get('count', 5)
        do_not_repeat = request.query_params.get('do_not_repeat')
        research = request.query_params.get('research')

        if not research:
            return response.Response(data={'error': 'Research ID is required'})

        try:
            research = BulkResearch.objects.get(id=research)
        except BulkResearch.DoesNotExist:
            return response.Response(data={'error': 'Research ID is invalid'})

        # retrieve new influencers
        flow = InfluencersFlow(key, model=model, count=count, do_not_repeat=do_not_repeat)
        resp = flow.discover_influencers()

        # retrieve health claims
        for influencer in resp:
            health_flow = HealthClaimsFlow(key, influencer, journals, comment, model=model)
            health_resp = health_flow.discover_health_claims()
            influencer['health_claims'] = health_resp
            ## overall trust score of influencer (avg)
            influencer['trust_score'] = round(sum([claim['trust_score'] for claim in health_resp]) / len(health_resp), 2)

        # save influencers to research
        for influencer in resp:
            influencer_obj = Influencer.objects.create(name=influencer.get('name'), bio=influencer.get('bio'), followers=influencer.get('followers'), trust_score=influencer.get('trust_score'))
            research.influencers.add(influencer_obj)

            for claim in influencer.get('health_claims'):
                try:
                    # Validate date format
                    if claim.get('date') and claim.get('date') != "Undated":
                        datetime.strptime(claim.get('date'), '%Y-%m-%d')
                except ValueError:
                    claim['date'] = None

                claim_obj = Claim.objects.create(influencer=influencer_obj, claim=claim.get('claim'), category=claim.get('category'), date=claim.get('date'), trust_score=claim.get('trust_score'), status=claim.get('status'))
                research_papers= claim.get('research_papers')
                for paper in research_papers:
                    date = paper.get('date')
                    try:
                        # Validate date format
                        if date and date != "Undated":
                            datetime.strptime(date, '%Y-%m-%d')
                        else:
                            date = None
                    except ValueError:
                        date = None
                    evidence_obj = ResearchPaper.objects.create(title=paper.get('title'), link=paper.get('link'), journal=paper.get('journal'), date=date)
                    if paper.get('is_evidence'):
                        claim_obj.evidence.add(evidence_obj)
                    else:
                        claim_obj.counter_evidence.add(evidence_obj)

        return response.Response(data=resp)

    @action(detail=False, methods=['post'])
    def check_influencer(self, request):
        key = request.query_params.get('key')
        model = request.query_params.get('model', 'sonar')
        influencer = request.query_params.get('influencer')
        max_claims = request.query_params.get('max_claims')
        min_claims = request.query_params.get('min_claims')

        # retrieve influencer
        flow = InfluencerFlow(key, influencer, model=model)
        resp = flow.check_influencer()

        # retrieve health claims
        health_flow = HealthClaimsFlow(key, influencer, max_claims=max_claims, min_claims=min_claims, model=model)
        health_resp = health_flow.discover_health_claims()
        resp['health_claims'] = health_resp
        ## overall trust score of influencer (avg)
        resp['trust_score'] = round(sum([claim['trust_score'] for claim in health_resp]) / len(health_resp), 2)

        return response.Response(data=resp)

    @action(detail=False, methods=['post'])
    def check_claim(self, request):
        key = request.query_params.get('key')
        model = request.query_params.get('model', 'sonar')
        claim = request.query_params.get('claim')
        journals = request.query_params.get('journals')

        # validate the claim
        flow = SingleClaimFlow(key, claim, journals, model=model)
        validation_result = flow.validate_claim()

        return response.Response(data=validation_result)

    @action(detail=False, methods=['post'])
    def begin_research(self, request):
        research_type = request.query_params.get('research_type')
        research = None
        if research_type == 'bulk':
            research = BulkResearch()
        elif research_type == 'single':
            research = SingleResearch()
        elif research_type == 'claim':
            research = ClaimResearch()

        if research:
            research.save()
            return response.Response(data={'research_id': research.id})

        else:
            return response.Response(data={'error': 'Invalid research type'})



