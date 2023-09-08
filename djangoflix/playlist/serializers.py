"""Serializer class for video API."""

from rest_framework import serializers
from core.models import Playlist, Video, TaggedItem
from tags.serializers import TaggedObjectRelatedField,TagSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    """Serializer for playlist."""
    # tags = TagSerializer(many=True, read_only=True)
    
    tags =TaggedObjectRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Playlist
        fields = ["title", "description", "id","tags"]
        read_only_fields = ["id"]
