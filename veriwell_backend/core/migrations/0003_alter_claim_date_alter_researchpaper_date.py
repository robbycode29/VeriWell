# Generated by Django 5.1.5 on 2025-01-28 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_bulkresearch_influencers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claim',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='researchpaper',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
