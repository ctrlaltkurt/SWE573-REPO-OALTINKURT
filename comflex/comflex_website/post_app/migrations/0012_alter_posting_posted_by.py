# Generated by Django 5.0.4 on 2024-04-27 19:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_app', '0011_remove_posting_attendees_posting_posted_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posting',
            name='posted_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='post_app.siteuser'),
        ),
    ]