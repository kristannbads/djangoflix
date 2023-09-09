from rest_framework import serializers
from core.models import TaggedItem


class TagSerializer(serializers.ModelSerializer):
    """Serializer for videos."""

    class Meta:
        model = TaggedItem
        fields = ["tag", "content_type", "object_id"]
        read_only_fields = ["id"]

    def to_representation(self, value):

        return f"{value.tag}"
