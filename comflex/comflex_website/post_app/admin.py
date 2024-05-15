from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Community, SiteUser, Posting, PostType, PostTypeField

admin.site.register(SiteUser)


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(Posting)
class PostingAdmin(admin.ModelAdmin):
    fields = (('name', 'community'), 'description', 'posted_by')
    list_display = ('name', 'community', 'description', 'posted_by')
    list_filter = ('community',)

class PostTypeFieldInline(admin.TabularInline):
    model = PostTypeField
    extra = 1

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return [f.name for f in self.model._meta.fields if f.name != 'post_type']
        return []

    def has_add_permission(self, request, obj):
        return False if obj and obj.fields.filter(is_fixed=True).exists() else True

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(PostType)
class PostTypeAdmin(admin.ModelAdmin):
    fields = ('post_type_name', 'community')
    list_display = ('post_type_name', 'community')
    list_filter = ('community',)
    inlines = [PostTypeFieldInline]

admin.site.register(PostTypeField)

class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('list_communities',)

    def list_communities(self, user):
        communities = user.communities.all()
        if communities:
            return ', '.join([community.name for community in communities])
        return 'No communities'
    list_communities.short_description = 'Communities'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
