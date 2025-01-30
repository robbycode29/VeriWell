from django.db import models


class AnalysisType(models.TextChoices):
    BULK = 'bulk',
    SINGLE = 'single',
    CLAIM = 'claim'


class Research(models.Model):
    analysis_type = models.CharField(max_length=255, choices=AnalysisType.choices, null=True, blank=True)
    failed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.analysis_type} - {self.created_at}'

    class Meta:
        abstract = True


class BulkResearch(Research):
    analysis_type = AnalysisType.BULK
    influencers = models.ManyToManyField('Influencer', related_name='bulk_researches', blank=True)


class SingleResearch(Research):
    analysis_type = AnalysisType.SINGLE
    influencer = models.ForeignKey('Influencer', related_name='single_researches', on_delete=models.CASCADE, null=True, blank=True)


class ClaimResearch(Research):
    analysis_type = AnalysisType.CLAIM
    claim = models.ForeignKey('Claim', related_name='claim_researches', on_delete=models.CASCADE, null=True, blank=True)


class Influencer(models.Model):
    name = models.CharField(max_length=255)
    profile_picture = models.URLField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    followers = models.IntegerField(null=True, blank=True)
    trust_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class Claim(models.Model):
    influencer = models.ForeignKey(Influencer, related_name='claims', on_delete=models.CASCADE)
    claim = models.TextField()
    source = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    trust_score = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    evidence = models.ManyToManyField('ResearchPaper', related_name='evidence_claims', blank=True)
    counter_evidence = models.ManyToManyField('ResearchPaper', related_name='counter_evidence_claims', blank=True)

    def __str__(self):
        return self.claim


class ResearchPaper(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    journal = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title
