from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# Register your models here.

from .models import Community
from .models import SiteUser
from .models import Posting
from .models import PostType


#admin.site.register(Community)
admin.site.register(SiteUser)
#admin.site.register(Posting)

@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
	list_display = ('name',
		)
	#list_display = ('name','address','phone')
	ordering=('name',)
	search_fields = ('name',)
	#search_fields = ('name','address')

@admin.register(Posting)
class PostingAdmin(admin.ModelAdmin):
	fields = (('name','community'),'description','posted_by')
	list_display = ('name','community','description','posted_by')
	list_filter = ('community',)


class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('list_communities',)

    def list_communities(self, user):
        communities = user.communities.all()
        if communities:
            return ', '.join([community.name for community in communities])
        return 'No communities'
    list_communities.short_description = 'Communities'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
