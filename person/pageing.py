# -*- coding: utf-8 -*-
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5000

    def get_paginated_response(self, data):
        total_count = self.page.paginator.count
        page_no = self.request.query_params.get('page', 1)
        page_size = self.request.query_params.get('page_size', self.page_size)
        pagination = dict(totalCount=total_count, pageNo=int(page_no), pageSize=page_size)
        all_data = dict(pagination=pagination, list=data)

        return Response(OrderedDict([
            ('status', status.HTTP_200_OK),
            ('info', 'success'),
            ('results', all_data),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
        ]))
