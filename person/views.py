# Create your views here.
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ngpyorient.base import Q
from ngrestframework.backends import OrientFilterBackend, OrientSearchBackend
from ngrestframework.pagination import NgPageNumberPagination
from ngrestframework.permissions import DjangoModelPermissionsStricted
from ngrestframework.renders import PandasJSONRenderer
from ngrestframework.viewsets import NodeModelViewSet
from person.filters import NgFilterBackend
from person.models import Person
from person.serializers import PersonSerializer
from rest_framework.parsers import BaseParser, JSONParser


class PersonViewSet(NodeModelViewSet):
    """"""
    serializer_class = PersonSerializer

    # filter_backends = (NgFilterBackend,)

    # queryset = Person.objects.filter(name='yuan1', age__lte=1).all()

    # 1 连续filter
    # queryset = Person.objects.filter(name__startswith='yuan', age__gte=1)
    # queryset.filter(name="yuan1", age__lte=1)

    # 2 all()
    # queryset = Person.objects.all()

    # 3 原生sql语句
    # queryset = Person.objects.raw("select from person")

    # queryset = Person.objects.raw(
    #     'select name,bothe("likes").in.name as car_name,bothe("likes").in.price as car_price from person')

    # queryset = Person.objects.raw('select name,bothe().in.name as car_name,bothe().in.@class as class_name from person').filter_result("car_name=='aodi'")
    # queryset = Person.objects.raw('select name,both("borned").name as province_name,both("likes").name as car_name from person').filter_result("car_name=='aodi' or province_name=='hubei'")
    queryset = Person.objects.raw(
        'select name,both("borned").name as province__name,both("likes").name as car__name ,both("likes").price as car__price from person')
    # 4 或查询
    # queryset = Person.objects.filter(Q(name__startswith='yuan') | Q(age__gte=1), Q(age__lte=21)).filter(
    #     Q(name__startswith='yu') | Q(age__gte=2), Q(age__lte=20)).filter(name__startswith='yua', age__gte=3)

    # queryset = Person.objects.filter(age__lte=1).filter(Q(name__startswith='yuan') | Q(age__gte=1))

    pagination_class = NgPageNumberPagination
    # permission_classes = (IsAuthenticated, DjangoModelPermissionsStricted)
    # permission_classes = ()
    # filter_backends = (OrientFilterBackend, OrientSearchBackend)
    # filter_backends = (OrientFilterBackend,)
    search_fields = ("name", "age")
    # renderer_classes = [PandasJSONRenderer]
