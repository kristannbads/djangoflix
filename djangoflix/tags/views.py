from tags.serializers import TaggedObjectRelatedField, TagSerializer

from rest_framework import authentication, permissions
from rest_framework import viewsets

from core.models import TaggedItem

# Create your views here.
class TagViewSet(viewsets.ModelViewSet):
    """View for tag APIs."""

    serializer_class = TagSerializer
    queryset = TaggedItem.objects.all()
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]