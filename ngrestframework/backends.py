"""

"""
import operator
from functools import reduce

from rest_framework.settings import api_settings

from ngpyorient.base import Q, QE
from ngpyorient.match import OPERATOR_TABLE
from ngpyorient.queryset import NgRawQuerySet


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


class OrientRawFilterBackend(object):
    """filter Ngrawqueryset"""

    def filter_queryset(self, request, queryset, view):
        filters = []
        if not isinstance(queryset, NgRawQuerySet):
            raise Exception("OrientRawFilterBackend should be used with NgRawQuerySet")
        query_params = dict(request.query_params.items())
        self.__format_params(query_params)
        for key, value in query_params.items():
            if key == api_settings.SEARCH_PARAM:
                continue
            statement = "{} == {}".format(key, value)
            filters.append(statement)
        filter_query = " and ".join(filters)
        queryset.filter_strs = "(" + queryset.filter_strs + ") and (" + filter_query + ")"
        return queryset

    def __format_params(self, params):
        """format paramat--->add quote when necessay"""
        for key, value in params.items():
            if type(value) == str:
                params[key] = "\'" + value + "\'"
