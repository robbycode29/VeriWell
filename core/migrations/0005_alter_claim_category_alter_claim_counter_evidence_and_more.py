# Generated by Django 5.1.5 on 2025-01-28 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_influencer_bio_alter_influencer_followers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='counter_evidence',
            field=models.ManyToManyField(blank=True, related_name='counter_evidence_claims', to='core.researchpaper'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='evidence',
            field=models.ManyToManyField(blank=True, related_name='evidence_claims', to='core.researchpaper'),
        ),
        migrations.AlterField(
            model_name='claim',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='claim',
            name='trust_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
