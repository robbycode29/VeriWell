from django.contrib import admin

from core.models import BulkResearch, SingleResearch, ClaimResearch, Influencer, Claim, ResearchPaper


admin.site.site_header = 'Veriwell Admin'

admin.site.site_title = 'Veriwell Admin Portal'

admin.site.index_title = 'Welcome to Veriwell Admin Portal'

admin.site.register(BulkResearch)
admin.site.register(SingleResearch)
admin.site.register(ClaimResearch)
admin.site.register(Influencer)
admin.site.register(Claim)
admin.site.register(ResearchPaper)