"""Serializer class for video API."""

from rest_framework import serializers

from core.models import Category


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category."""

    class Meta:
        model = Category
        fields = ["title", "id"]
        read_only_fields = ["id"]

    def to_representation(self, value):

        return f"{value.title}"
