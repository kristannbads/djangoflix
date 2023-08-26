# Generated by Django 4.0.10 on 2023-08-26 04:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_video_videoallproxy_videopublishedproxy"),
    ]

    operations = [
        migrations.AddField(
            model_name="video",
            name="user",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]