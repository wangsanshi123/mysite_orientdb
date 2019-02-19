"""

"""
from rest_framework.filters import BaseFilterBackend


class NgFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        """
        SELECT EXPAND( BOTH('Friend').out('Eat') ) FROM Person
        WHERE name='Luca'
        to = "b_friend__o_eat"
        name="zhang"

          """
        params = request.query_params
        # sql = queryset.sql
        return queryset
