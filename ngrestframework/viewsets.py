"""

"""
import re
from logging import exception

from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from ngpyorient import ng_node, ng_relationship
from ngpyorient.ng_node import NgNode
from ngpyorient.ng_relationship import NgRelationship
from ngpyorient.queryset import NgQuerySet, NgRawQuerySet
from ngrestframework.mixinx import UpdateModelMixin, DestroyModelMixin, RetrieveModelMixin, CreateModelMixin, \
    UpdateModelMixinWithNone, CreateModelMixinWithNone, PandasMixin
from ngrestframework.renders import NgRender, PandasJSONRenderer


class GenericViewSet(GenericViewSet):
    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
                "'%s' should either include a `queryset` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, NgQuerySet) or isinstance(queryset, NgRawQuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    lookup_field = 'rid'
    renderer_classes = [NgRender]

    def format_result(self, result, kclass):
        """
        @deprecated:this method is deprecated,you should use serializer instead
        format result avoiding using serializer of rest framework(here we can get any property of any class
        without define the serializer)
        """
        if ng_node.NgNode in kclass.__mro__:
            data = result.__dict__["_OrientRecord__o_storage"]
            data["rid"] = result.__dict__["_OrientRecord__rid"]
            for key in data.copy().keys():
                if re.match(r"(out|in|both).*?", key):
                    data.pop(key)

        elif ng_relationship.NgRelationship in kclass.__mro__:
            data = result.__dict__["_OrientRecord__o_storage"]
            data["rid"] = result.__dict__["_OrientRecord__rid"]
            data = {key: value.__str__() for key, value in data.items()}
        else:
            raise exception("the class {} is either vertex nor edge".format(kclass))

        return data


class ModelViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    pass


class ModelViewSetWithNone(CreateModelMixinWithNone,
                           RetrieveModelMixin,
                           UpdateModelMixinWithNone,
                           DestroyModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    pass


class NodeModelViewSet(ModelViewSet):
    """

    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """


class RelationModelViewSet(ModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    lookup_field = 'class'

    def list(self, request, *args, **kwargs):
        try:
            NgNode.registry.pop("ngnode")
            NgRelationship.registry.pop("ngrelationship")
        except:
            pass

        NgNode.registry.update(NgRelationship.registry)
        data = {}
        for key in NgNode.registry.keys():
            data[key] = reverse('relations-list', request=request) + key

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        """list all items of vertexs or edges according to kwargs(class)"""

        NgNode.registry.update(NgRelationship.registry)
        kclass = NgNode.registry[kwargs["class"]]
        queryset = kclass.objects.all()
        result = [self.format_result(item, kclass) for item in queryset]

        return Response(result)


class NodeModelViewSetWithNone(ModelViewSetWithNone):
    """

    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    lookup_field = 'rid'


class PandasViewBase(PandasMixin):
    renderer_classes = [PandasJSONRenderer]
    pagination_class = None
