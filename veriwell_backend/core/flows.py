from core.perplexity import Perplexity
from pydantic import BaseModel
from datetime import datetime


class Influencer(BaseModel):
    name: str
    bio: str
    followers: int


class Flow:
    """
    Creates interaction flows with the Perplexity API
    """
    def __init__(self, key):
        self.perplexity = Perplexity(key)

    class AnswerFormat(BaseModel):
        """
        Answer format for the Perplexity API
        """
        pass


class InfluencerFlow(Flow):
    """
    Manages the interaction flow to retrieve an influencer
    """

    def __init__(self, key, influencer):
        super().__init__(key)
        self.influencer = influencer
        self.payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": (
                    f"Find information about the influencer {influencer}."
                    "Please output a JSON object with the following keys: "
                    "name, bio (detailed), followers (int)."
                    "Do not include any other text in the response."
                    "Return a valid raw JSON response."
                )},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self.AnswerFormat.model_json_schema()},
            },
        }

    def check_influencer(self):
        """
        Discover an influencer
        """
        response = self.perplexity.ask(self.payload)
        return response

    class AnswerFormat(BaseModel):
        influencer: Influencer


class InfluencersFlow(Flow):
    """
    Manages the interaction flow to retrieve influencers
    """

    def __init__(self, key):
        super().__init__(key)
        self.payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": (
                    "Find top influencers in the health industry."
                    "Top influencers are those with the most followers."
                    f"Please output a JSON list of objects with the following keys: "
                    "name, bio (detailed), followers (int)."
                    "Do not include any other text in the response."
                    "Return a valid raw JSON response."
                    "Return a maximum of 5 influencers."
                )},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self.AnswerFormat.model_json_schema()},
            },
        }

    def discover_influencers(self):
        """
        Discover new influencers
        """
        response = self.perplexity.ask(self.payload)
        return response

    class AnswerFormat(BaseModel):
        influencers: list[Influencer]


class HealthClaim(BaseModel):
    claim: str
    category: str
    evidence: list[str]
    counter_evidence: list[str]
    date: datetime
    trust_score: float
    status: str


class HealthClaimsFlow(Flow):
    """
    Manages the interaction flow to retrieve health claims for an influencer
    """

    def __init__(self, key, influencer, journals=None, comment=None, max_claims=5, min_claims=1):
        super().__init__(key)
        self.influencer = influencer
        self.journals = journals or ["any", "Pubmed Central", "Nature", "Science", "Cell", "The Lancet", "New England Journal of Medicine", "JAMA"]
        self.comment = comment
        self.max_claims = max_claims
        self.min_claims = min_claims
        self.payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be precise and concise. Search references thoroughly"},
                {"role": "user", "content": (
                    f"Find latest health claims for the influencer {influencer}."
                    "Please output a JSON list of objects with the following keys: "
                    "claim, category, evidence (links to research papers if exists else []; must have word match), counter_evidence (links to research papers if exists else []; must have word match), date (yyyy-mm-dd)."
                    f"Evidence and counter evidence should come from the following trusted scientific journals: {', '.join(self.journals)}."
                    f"Notes for research assistant: {self.comment}"
                    "Do not include any other text in the response."
                    "Return a valid raw JSON response."
                    f"Return a maximum of {self.max_claims} health claims."
                    f"Return a minimum of {self.min_claims} health claims."
                )},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self.AnswerFormat.model_json_schema()},
            },
        }

    def discover_health_claims(self):
        """
        Discover health claims for an influencer
        """
        response = self.perplexity.ask(self.payload)
        health_claims = [self.validate_claim(claim) for claim in response]
        return health_claims

    def validate_claim(self, claim):
        """
        Validate or invalidate the claim based on research papers
        """
        research_flow = ResearchPapersFlow(self.perplexity.API_KEY, claim['claim'], self.journals)
        validation_result = research_flow.validate_claim()
        claim.update(validation_result)
        return claim

    class AnswerFormat(BaseModel):
        health_claims: list[HealthClaim]


class ResearchPaper(BaseModel):
    title: str
    link: str
    journal: str
    date: datetime
    is_evidence: bool


class ResearchPapersFlow(Flow):
    """
    Manages the interaction flow to retrieve research papers and validate/invalidate a claim
    """

    def __init__(self, key, claim, journals=None):
        super().__init__(key)
        self.claim = claim
        self.journals = journals or ["any", "Pubmed Central", "Nature", "Science", "Cell", "The Lancet", "New England Journal of Medicine", "JAMA"]
        self.payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be precise and concise. Search references thoroughly"},
                {"role": "user", "content": (
                    f"Find research papers that validate or invalidate the claim: '{claim}'."
                    "Please output a JSON list of objects with the following keys: "
                    "title, link, journal, date (yyyy-mm-dd), is_evidence (true if evidence, false if counter-evidence)."
                    f"Research papers should come from the following trusted scientific journals: {', '.join(self.journals)}."
                    "Do not include any other text in the response."
                    "Return a valid raw JSON response."
                )},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self.AnswerFormat.model_json_schema()},
            },
        }

    def retrieve_research_papers(self):
        """
        Retrieve research papers for the claim
        """
        response = self.perplexity.ask(self.payload)
        return response

    def validate_claim(self):
        """
        Validate or invalidate the claim based on research papers
        """
        research_papers = self.retrieve_research_papers()
        evidence_links = [paper['link'] for paper in research_papers if paper['is_evidence']]
        counter_evidence_links = [paper['link'] for paper in research_papers if not paper['is_evidence']]

        evidence_count = len(evidence_links)
        counter_evidence_count = len(counter_evidence_links)
        total_count = evidence_count + counter_evidence_count

        if total_count == 0:
            trust_score = 0.5  # Neutral score if there is no evidence or counter-evidence
        else:
            trust_score = round(evidence_count / total_count, 2)

        status = self.determine_status(trust_score)
        return {
            "claim": self.claim,
            "trust_score": trust_score,
            "status": status,
            "evidence": evidence_links,
            "counter_evidence": counter_evidence_links,
            "research_papers": research_papers
        }

    def determine_status(self, trust_score):
        """
        Determine the status based on the trust score
        """
        if trust_score > 0.75:
            return "verified"
        elif trust_score < 0.25:
            return "debunked"
        else:
            return "questionable"

    class AnswerFormat(BaseModel):
        research_papers: list[ResearchPaper]


class SingleClaimFlow(Flow):
    """
    Manages the interaction flow to validate a single claim
    """

    def __init__(self, key, claim, journals=None):
        super().__init__(key)
        self.claim = claim
        self.journals = journals or ["any", "Pubmed Central", "Nature", "Science", "Cell", "The Lancet", "New England Journal of Medicine", "JAMA"]
        self.payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": "Be precise and concise. Search references thoroughly"},
                {"role": "user", "content": (
                    f"Find research papers that validate or invalidate the claim: '{claim}'."
                    "Please output a JSON list of objects with the following keys: "
                    "title, link, journal, date (yyyy-mm-dd), is_evidence (true if evidence, false if counter-evidence)."
                    f"Research papers should come from the following trusted scientific journals: {', '.join(self.journals)}."
                    "Do not include any other text in the response."
                    "Return a valid raw JSON response."
                )},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"schema": self.AnswerFormat.model_json_schema()},
            },
        }

    def validate_claim(self):
        """
        Validate or invalidate the claim based on research papers
        """
        research_flow = ResearchPapersFlow(self.perplexity.API_KEY, self.claim, self.journals)
        validation_result = research_flow.validate_claim()
        return validation_result

    class AnswerFormat(BaseModel):
        research_papers: list[ResearchPaper]