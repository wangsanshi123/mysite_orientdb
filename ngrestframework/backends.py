"""
a
"""
import operator
import re
from functools import reduce

from rest_framework.settings import api_settings

from ngpyorient.base import Q, QE
from ngpyorient.match import OPERATOR_TABLE
from ngpyorient.queryset import NgRawQuerySet
from django.db import models
from rest_framework.compat import coreapi, coreschema, distinct, guardian
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from ngrestframework import compat
import warnings


class OrientFilterBackend(object):

    def filter_queryset(self, request, queryset, view):

        for key, value in request.query_params.items():
            if key == api_settings.SEARCH_PARAM:
                continue
            if "__" in key:
                prop, operator = key.rsplit("__")
                try:
                    OPERATOR_TABLE[operator]
                except KeyError:
                    queryset.filter(QE(**{key: value}))
            queryset.filter(Q(**{key: value}))
        return queryset


class OrientSearchBackend(object):
    search_param = api_settings.SEARCH_PARAM

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        return params.split(',')

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups_q = [
            self.construct_search(search_field)
            for search_field in search_fields
            if self.isQ(search_field)
        ]
        orm_lookups_qe = [
            self.construct_search(search_field)
            for search_field in search_fields
            if not self.isQ(search_field)
        ]
        for search_term in search_terms:
            queries_q = [
                Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups_q
            ]

            queries_qe = [
                QE(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups_qe
            ]
            if len(queries_q) > 0:
                queryset = queryset.filter(reduce(operator.or_, queries_q))
            if len(queries_qe) > 0:
                queryset = queryset.filter(reduce(operator.or_, queries_qe))

        return queryset

    def construct_search(self, field_name):
        return "__".join([field_name, "contains"])

    def isQ(self, field):
        """judge whether is Q or QE"""
        return len(field.split("__")) == 1

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]


class OrientRawFilterBackend(object):
    """filter Ngrawqueryset"""

    def filter_queryset(self, request, queryset, view):
        filter_fields = getattr(view, 'filter_fields', None)

        filters = []
        if not isinstance(queryset, NgRawQuerySet):
            raise Exception("OrientRawFilterBackend should be used with NgRawQuerySet")
        query_params = dict(request.query_params.items())
        # self.__format_params(query_params)
        for key, value in query_params.items():
            if key == api_settings.SEARCH_PARAM:
                continue

            pass
        return queryset

    def __format_params(self, params):
        """format paramat--->add quote when necessay"""
        for key, value in params.items():
            if type(value) == str:
                params[key] = "\'" + value + "\'"

    def get_schema_fields(self, view):
        # This is not compatible with widgets where the query param differs from the
        # filter's attribute name. Notably, this includes `MultiWidget`, where query
        # params will be of the format `<name>_0`, `<name>_1`, etc...
        assert compat.coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert compat.coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'

        filter_class = getattr(view, 'filter_class', None)
        if filter_class is None:
            try:
                filter_class = self.get_filter_class(view, view.get_queryset())
            except Exception:
                warnings.warn(
                    "{} is not compatible with schema generation".format(view.__class__)
                )
                filter_class = None

        return [] if not filter_class else [
            compat.coreapi.Field(
                name=field_name,
                required=field.extra['required'],
                location='query',
                schema=self.get_coreschema_field(field)
            ) for field_name, field in filter_class.base_filters.items()
        ]


class OrientRawSearchBackend(object):
    search_param = api_settings.SEARCH_PARAM
    template = 'rest_framework/filters/search.html'
    search_title = _('Search')
    search_description = _('A search term.')

    def get_search_terms(self, request):
        params = request.query_params.get(self.search_param, '')
        return params.replace(',', ' ').split()

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)

        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(search_field)
            for search_field in search_fields
        ]
        conditions = []
        for search_term in search_terms:
            queries = []
            for orm_lookup in orm_lookups:
                queries.append(Q(**{orm_lookup: "%" + search_term + "%"}))

            conditions.append(reduce(operator.or_, queries))
        return queryset.filter(reduce(operator.and_, conditions))

    def construct_search(self, field_name):
        result = " ".join([field_name, "like"])
        return result

    def isQ(self, field):
        """judge whether is Q or QE"""
        return len(field.split("__")) == 1

    def is_relation_node(self, field_name):
        """
        whether is relative node
        true:is relative node
        false:is current node
        """
        if re.match("(in)|(out)\(.*?\).*?", field_name, re.IGNORECASE):
            return True
        else:
            return False

    def get_schema_fields(self, view):
        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        return [
            coreapi.Field(
                name=self.search_param,
                required=False,
                location='query',
                schema=coreschema.String(
                    title=force_text(self.search_title),
                    description=force_text(self.search_description)
                )
            )
        ]
