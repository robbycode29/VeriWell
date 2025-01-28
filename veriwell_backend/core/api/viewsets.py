from datetime import datetime

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework import response
from core.api.serializers import InfluencerSerializer, ClaimSerializer

from core.flows import InfluencerFlow, InfluencersFlow, HealthClaimsFlow, SingleClaimFlow
from core.models import BulkResearch, SingleResearch, ClaimResearch, Influencer, Claim, ResearchPaper
from core.utils import are_strings_similar

from django.conf import settings


DEFAULT_PERPLEXITY_KEY = settings.PERPLEXITY_API_KEY


class InfluencersViewSet(viewsets.ModelViewSet):
    queryset = Influencer.objects.all()
    serializer_class = InfluencerSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def check_bulk(self, request):
        key = request.query_params.get('key', DEFAULT_PERPLEXITY_KEY)
        model = request.query_params.get('model', 'sonar')
        journals = request.query_params.get('journals')
        comment = request.query_params.get('comment')
        count = request.query_params.get('count', 5)
        do_not_repeat = request.query_params.get('do_not_repeat')
        research = request.query_params.get('research')
        timeframe = request.query_params.get('timeframe', 'latest')

        if not research:
            return response.Response(data={'error': 'Research ID is required'}, status=400)

        try:
            research = BulkResearch.objects.get(id=research)
        except BulkResearch.DoesNotExist:
            return response.Response(data={'error': 'Research ID is invalid'}, status=400)

        # retrieve new influencers
        flow = InfluencersFlow(key, model=model, count=count, do_not_repeat=do_not_repeat)
        resp = flow.discover_influencers()

        # retrieve health claims
        for influencer in resp:
            health_flow = HealthClaimsFlow(key, influencer, journals, comment, model=model, timeframe=timeframe)
            health_resp = health_flow.discover_health_claims()
            influencer['health_claims'] = health_resp
            ## overall trust score of influencer (avg)
            influencer['trust_score'] = round(sum([claim['trust_score'] for claim in health_resp]) / len(health_resp), 2)

        # save influencers to research
        for influencer in resp:
            influencer_obj = Influencer.objects.filter(name=influencer.get('name'))
            if influencer_obj:
                influencer_obj = influencer_obj.first()
            if not influencer_obj:
                influencer_obj = Influencer.objects.create(name=influencer.get('name'), bio=influencer.get('bio'), followers=influencer.get('followers'), trust_score=influencer.get('trust_score'), profile_picture=influencer.get('profile_picture'))
            research.influencers.add(influencer_obj)

            for claim in influencer.get('health_claims'):
                # Check for duplicate claims using Levenshtein distance
                existing_claims = Claim.objects.filter(influencer=influencer_obj)
                is_duplicate = False
                for existing_claim in existing_claims:
                    if are_strings_similar(claim.get('claim'), existing_claim.claim):
                        is_duplicate = True
                        break

                if is_duplicate:
                    continue

                try:
                    # Validate date format
                    if claim.get('date') and claim.get('date') != "Undated":
                        datetime.strptime(claim.get('date'), '%Y-%m-%d')
                except ValueError:
                    claim['date'] = None

                claim_obj = Claim.objects.create(influencer=influencer_obj, claim=claim.get('claim'), category=claim.get('category'), date=claim.get('date'), trust_score=claim.get('trust_score'), status=claim.get('status'))
                research_papers = claim.get('research_papers')
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
                    link = paper.get('link')
                    if link:
                        evidence_obj = ResearchPaper.objects.create(title=paper.get('title'), link=paper.get('link'), journal=paper.get('journal'), date=date)
                        if paper.get('is_evidence'):
                            claim_obj.evidence.add(evidence_obj)
                        else:
                            claim_obj.counter_evidence.add(evidence_obj)

            # Update influencer trust score
            all_claims = Claim.objects.filter(influencer=influencer_obj)
            if all_claims.exists():
                avg_trust_score = round(sum([claim.trust_score for claim in all_claims]) / len(all_claims), 2)
                influencer_obj.trust_score = avg_trust_score
                influencer_obj.save()

        return response.Response(data=resp)

    @action(detail=False, methods=['post'])
    def check_influencer(self, request):
        key = request.query_params.get('key', DEFAULT_PERPLEXITY_KEY)
        model = request.query_params.get('model', 'sonar')
        influencer = request.query_params.get('influencer')
        count = request.query_params.get('count', 5)
        research_id = request.query_params.get('research')
        timeframe = request.query_params.get('timeframe', 'latest')

        if not research_id:
            return response.Response(data={'error': 'Research ID is required'}, status=400)

        try:
            research = SingleResearch.objects.get(id=research_id)
        except SingleResearch.DoesNotExist:
            return response.Response(data={'error': 'Research ID is invalid'}, status=400)

        # retrieve influencer
        flow = InfluencerFlow(key, influencer, model=model)
        resp = flow.check_influencer()

        # retrieve health claims
        health_flow = HealthClaimsFlow(key, influencer, count=count, model=model, timeframe=timeframe)
        health_resp = health_flow.discover_health_claims()
        resp['health_claims'] = health_resp
        ## overall trust score of influencer (avg)
        resp['trust_score'] = round(sum([claim['trust_score'] for claim in health_resp]) / len(health_resp), 2)

        # save influencer to research
        influencer_obj = Influencer.objects.filter(name=resp.get('name'))
        if influencer_obj:
            influencer_obj = influencer_obj.first()
        if not influencer_obj:
            influencer_obj = Influencer.objects.create(name=resp.get('name'), bio=resp.get('bio'), followers=resp.get('followers'), trust_score=resp.get('trust_score'), profile_picture=resp.get('profile_picture'))
        research.influencer = influencer_obj
        research.save()

        for claim in resp.get('health_claims'):
            # Check for duplicate claims using Levenshtein distance
            existing_claims = Claim.objects.filter(influencer=influencer_obj)
            is_duplicate = False
            for existing_claim in existing_claims:
                if are_strings_similar(claim.get('claim'), existing_claim.claim):
                    is_duplicate = True
                    break

            if is_duplicate:
                continue

            try:
                # Validate date format
                if claim.get('date') and claim.get('date') != "Undated":
                    datetime.strptime(claim.get('date'), '%Y-%m-%d')
            except ValueError:
                claim['date'] = None

            claim_obj = Claim.objects.create(influencer=influencer_obj, claim=claim.get('claim'), category=claim.get('category'), date=claim.get('date'), trust_score=claim.get('trust_score'), status=claim.get('status'))
            research_papers = claim.get('research_papers')
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
                link = paper.get('link')
                if link:
                    evidence_obj = ResearchPaper.objects.create(title=paper.get('title'), link=paper.get('link'), journal=paper.get('journal'), date=date)
                    if paper.get('is_evidence'):
                        claim_obj.evidence.add(evidence_obj)
                    else:
                        claim_obj.counter_evidence.add(evidence_obj)

        # Update influencer trust score
        all_claims = Claim.objects.filter(influencer=influencer_obj)
        if all_claims.exists():
            avg_trust_score = round(sum([claim.trust_score for claim in all_claims]) / len(all_claims), 2)
            influencer_obj.trust_score = avg_trust_score
            influencer_obj.save()

        return response.Response(data=resp)

    @action(detail=False, methods=['post'])
    def check_claim(self, request):
        key = request.query_params.get('key', DEFAULT_PERPLEXITY_KEY)
        model = request.query_params.get('model', 'sonar')
        claim = request.query_params.get('claim')
        journals = request.query_params.get('journals')

        # validate the claim
        flow = SingleClaimFlow(key, claim, journals, model=model)
        validation_result = flow.validate_claim()

        # Create or get the Default influencer
        default_influencer, created = Influencer.objects.get_or_create(name="Default")

        # Ensure link is not null before creating ResearchPaper objects
        research_papers = []
        evidence_list = []
        counter_evidence_list = []
        for paper in validation_result.get('research_papers', []):
            date = paper.get('date')
            try:
                # Validate date format
                if date and date != "Undated":
                    datetime.strptime(date, '%Y-%m-%d')
                else:
                    date = None
            except ValueError:
                date = None
            link = paper.get('link')
            if link:
                evidence_obj = ResearchPaper.objects.create(title=paper.get('title'), link=link, journal=paper.get('journal'), date=date)
                research_papers.append({
                    'title': evidence_obj.title,
                    'link': evidence_obj.link,
                    'journal': evidence_obj.journal,
                    'date': evidence_obj.date
                })
                if paper.get('is_evidence'):
                    evidence_list.append(evidence_obj)
                else:
                    counter_evidence_list.append(evidence_obj)

        # Create the claim and associate it with the Default influencer
        claim_obj = Claim.objects.create(
            influencer=default_influencer,
            claim=validation_result.get('claim'),
            category=validation_result.get('category'),
            date=datetime.now(),
            trust_score=validation_result.get('trust_score'),
            status=validation_result.get('status')
        )
        claim_obj.evidence.set(evidence_list)
        claim_obj.counter_evidence.set(counter_evidence_list)

        # Create and associate ClaimResearch with the claim
        claim_research = ClaimResearch.objects.create(claim=claim_obj)

        # Update validation_result with serializable research papers
        validation_result['research_papers'] = research_papers

        return response.Response(status=200, data={'success': 'Claim checked successfully'})

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


class ClaimsViewSet(viewsets.ModelViewSet):
    serializer_class = ClaimSerializer

    def get_queryset(self):
        influencer_name = self.request.query_params.get('influencer_name') or self.request.data.get('influencer_name')
        if influencer_name:
            return Claim.objects.filter(influencer__name=influencer_name)
        return Claim.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

