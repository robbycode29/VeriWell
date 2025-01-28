from django.db import models


class AnalysisType(models.TextChoices):
    BULK = 'bulk',
    SINGLE = 'single',
    CLAIM = 'claim'


class Research(models.Model):
    analysis_type = models.CharField(max_length=255, choices=AnalysisType.choices, null=True, blank=True)
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
    bio = models.TextField()
    followers = models.IntegerField()
    trust_score = models.FloatField()


class Claim(models.Model):
    influencer = models.ForeignKey(Influencer, related_name='claims', on_delete=models.CASCADE)
    claim = models.TextField()
    category = models.CharField(max_length=255)
    date = models.DateField(null=True, blank=True)
    trust_score = models.FloatField()
    status = models.CharField(max_length=50)
    evidence = models.ManyToManyField('ResearchPaper', related_name='evidence_claims')
    counter_evidence = models.ManyToManyField('ResearchPaper', related_name='counter_evidence_claims')


class ResearchPaper(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    journal = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
