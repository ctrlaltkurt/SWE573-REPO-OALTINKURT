# Generated by Django 5.0.4 on 2024-04-23 12:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Community',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Community Name')),
                ('address', models.CharField(max_length=300)),
                ('zip_code', models.CharField(max_length=15, verbose_name='Zip Code')),
                ('phone', models.CharField(blank=True, max_length=25, verbose_name='Contact Phone')),
                ('web', models.URLField(blank=True, verbose_name='Website Address')),
                ('email_address', models.EmailField(blank=True, max_length=254, verbose_name='Email Address')),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='User',
            new_name='RegularUser',
        ),
        migrations.CreateModel(
            name='Posting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Post Name')),
                ('posting_date', models.DateTimeField(verbose_name='Event Date')),
                ('manager', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('attendees', models.ManyToManyField(blank=True, to='post_app.regularuser')),
                ('community', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='post_app.community')),
            ],
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.DeleteModel(
            name='Venue',
        ),
    ]