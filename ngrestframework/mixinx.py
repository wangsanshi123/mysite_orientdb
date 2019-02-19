"""

"""
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from ngpyorient.match import process_filter_args
from ngpyorient.queryset import NgQuerySet
from ngrestframework.renders import PandasBaseRenderer
from ngrestframework.serializers import PandasSerializer


class UpdateModelMixin(object):
    """
     Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.kwargs, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class RetrieveModelMixin(object):
    """
    Retrieve a model instance.
    """

    def retrieve(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if isinstance(queryset, NgQuerySet):
            # clear existed filterd conditions
            queryset.filters.clear()
            queryset.manager.filters.clear()
            queryset.qs.clear()
            # add new filterd conditions(here is record_id)
            filter_origin, filter_destination = process_filter_args(queryset.manager.source_class, kwargs)
            if filter_origin:
                queryset.filters.append(filter_origin)

            results = queryset.execute()
            if not results or not len(results):
                raise NotFound(detail="{} is not found".format(kwargs.values()))
            instance = results[0]
            serializer = self.get_serializer(instance)
        # get result by record_id from ngrawqueryset
        else:
            if "where" in queryset.raw_query:
                queryset.raw_query = queryset.raw_query + " and @rid = {}".format(kwargs["rid"])
            else:
                queryset.raw_query = queryset.raw_query + " where @rid = {}".format(kwargs["rid"])

            serializer = self.get_serializer(queryset, many=True)
            pass
        return Response(serializer.data)


class CreateModelMixin(object):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()


class DestroyModelMixin(object):
    """
    Destroy a model instance.
    """

    def destroy(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        results = queryset.manager.source_class.objects.filter(rid=kwargs["rid"]).delete()
        if not results[0]:
            raise NotFound()
        # return Response(status=status.HTTP_204_NO_CONTENT)
        return Response()


class UpdateModelMixinWithNone(object):
    """
     Update a model instance. do not return data to response
    """

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.kwargs, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())

    def perform_create(self, serializer):
        serializer.save()


class CreateModelMixinWithNone(object):
    """ do not return data to response"""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())

    def perform_create(self, serializer):
        serializer.save()


class PandasMixin(object):
    pandas_serializer_class = PandasSerializer

    def with_list_serializer(self, cls):
        meta = getattr(cls, 'Meta', object)
        if getattr(meta, 'list_serializer_class', None):
            return cls

        class SerializerWithListSerializer(cls):
            class Meta(meta):
                list_serializer_class = self.pandas_serializer_class

        return SerializerWithListSerializer

    def get_serializer_class(self):

        # c.f rest_framework.generics.GenericAPIView
        # (not using super() since this is a mixin class)
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )

        renderer = self.request.accepted_renderer
        if hasattr(renderer, 'get_default_renderer'):
            # BrowsableAPIRenderer
            renderer = renderer.get_default_renderer(self)

        if isinstance(renderer, PandasBaseRenderer):
            return self.with_list_serializer(self.serializer_class)
        else:
            return self.serializer_class
