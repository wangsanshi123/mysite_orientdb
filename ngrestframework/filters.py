# -*- coding:utf-8 -*-
# create_time: 2018/11/19 19:59
__author__ = 'brad'

from rest_framework.filters import SearchFilter
from ngpyorient.base import Q
from django.db.models.constants import LOOKUP_SEP
import operator
from functools import reduce

class NgSearchFilter(SearchFilter):
    # todo: 修改为不按忽略大小写去匹配, 因为这样才不会返回空值
    lookup_prefixes = {
        '^': 'startswith',
        '=': 'exact',
        '@': 'search',
        '$': 'regex',
    }

    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_terms = self.get_search_terms(request)
        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(search_field) for search_field in search_fields]

        base = queryset
        conditions = []
        for search_term in search_terms:
            queries = [
                Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))

        return queryset