"""Views for Category API."""
from categories.serializers import CategorySerializer

from rest_framework import authentication, permissions
from rest_framework import viewsets

from core.models import Category


class CategoryViewSet(viewsets.ModelViewSet):
    """View for playlist APIs."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
