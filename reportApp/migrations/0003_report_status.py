# Generated by Django 4.2.13 on 2024-07-20 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reportApp', '0002_rename_user_report_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
