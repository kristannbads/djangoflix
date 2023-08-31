"""Serializer class for video API."""

from rest_framework import serializers

from core.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serializer for videos."""

    class Meta:
        model = Video
        fields = ["title", "description", "id", "video_id"]
        read_only_fields = ["id"]
