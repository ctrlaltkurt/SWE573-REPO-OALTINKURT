from django.contrib import admin

# Register your models here.

from .models import Community
from .models import SiteUser
from .models import Posting

#admin.site.register(Community)
admin.site.register(SiteUser)
#admin.site.register(Posting)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
	list_display = ('name',)
	#list_display = ('name','address','phone')
	ordering=('name',)
	search_fields = ('name',)
	#search_fields = ('name','address')

@admin.register(Posting)
class PostingAdmin(admin.ModelAdmin):
	fields = (('name','community'),'description','posted_by')
	list_display = ('name','community','description','posted_by')
	list_filter = ('community',)

