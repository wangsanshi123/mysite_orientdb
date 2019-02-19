# Create your views here.
from ngpyorient.base import Out, Both
from ngrestframework.viewsets import RelationModelViewSet
from person.models import Likes
from relations.serializers import RelationshipsCreateSerializer


class RelationsViewSet(RelationModelViewSet):
    """"""
    queryset = Likes.objects.all()
    serializer_class = RelationshipsCreateSerializer
