# Generated by Django 5.0.4 on 2024-04-24 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post_app', '0006_remove_posting_posting_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='regularuser',
            name='email',
            field=models.EmailField(blank=True, max_length=30, verbose_name='User Email'),
        ),
    ]
