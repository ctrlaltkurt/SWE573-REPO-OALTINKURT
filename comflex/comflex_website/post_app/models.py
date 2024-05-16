import json
from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Community(models.Model):
    name = models.CharField('Community Name', max_length=120)
    is_public = models.BooleanField(default=True, help_text="Check if the community is public!")
    creation_date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    owner_id = models.IntegerField('Community Owner', blank=False, default=1)
    owner_username = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL)
    members = models.ManyToManyField(User, related_name='communities', blank=True)

    def __str__(self):
        return self.name

class SiteUser(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField('User Email', max_length=30, blank=True)
    member_of = models.ForeignKey(Community, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

class PostType(models.Model):
    post_type_name = models.CharField(max_length=100)
    community = models.ForeignKey(Community, related_name='post_types', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.post_type_name}"

class PostTypeField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
    )
    post_type = models.ForeignKey(PostType, related_name='fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=50, choices=FIELD_TYPES)
    is_fixed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.field_name} ({self.get_field_type_display()})"

class Posting(models.Model):
    name = models.CharField('Post Name', max_length=120)
    posting_date = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey(Community, blank=False, null=False, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    posted_by = models.ForeignKey(User, blank=False, null=True, on_delete=models.SET_NULL)
    custom_fields = models.TextField(blank=True, default='{}')  # Use TextField for custom fields
    post_type = models.ForeignKey(PostType, related_name='postings', on_delete=models.CASCADE, null=True)  # Allow null for now to handle migration

    def __str__(self):
        return self.name

    def get_custom_fields(self):
        try:
            return json.loads(self.custom_fields)
        except json.JSONDecodeError:
            return {}

    def set_custom_fields(self, fields):
        for key, value in fields.items():
            if isinstance(value, (datetime, date)):
                fields[key] = value.isoformat()
        self.custom_fields = json.dumps(fields)

@receiver(post_save, sender=Community)
def create_default_post_type(sender, instance, created, **kwargs):
    if created:
        default_post_type = PostType.objects.create(
            post_type_name='Default Post', community=instance
        )
        PostTypeField.objects.create(
            post_type=default_post_type, field_name='post title', field_type='text', is_fixed=True
        )
        PostTypeField.objects.create(
            post_type=default_post_type, field_name='description', field_type='text', is_fixed=True
        )
