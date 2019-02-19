# -*- coding:utf-8 -*-
# create_time: 2018/11/19 11:12
__author__ = 'brad'

from rest_framework.pagination import PageNumberPagination, InvalidPage
from ngpyorient.paginator import NgpyorientPaginator
from ngpyorient.queryset import NgQuerySet, NgRawQuerySet
from rest_framework.exceptions import NotFound
from django.utils import six
from rest_framework.response import Response
from collections import OrderedDict

class NgPageNumberPagination(PageNumberPagination):

    ngpyorient_paginator_class = NgpyorientPaginator
    page_size_query_param = "pagesize"

    page_size = 2
    max_page_size = 5000

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        self.real_page_size = self.get_page_size(request)
        if not self.real_page_size:
            return None

        # todo:这里区分是用哪个分页
        if isinstance(queryset, (NgRawQuerySet, NgQuerySet)):
            paginator = self.ngpyorient_paginator_class(queryset, self.real_page_size)
        else:
            paginator = self.django_paginator_class(queryset, self.real_page_size)
        self.real_page_number = request.query_params.get(self.page_query_param, 1)
        if self.real_page_number in self.last_page_strings:
            self.real_page_number = paginator.num_pages

        try:
            self.page = paginator.page(self.real_page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=self.real_page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('page', self.real_page_number),
            ('pagesize', self.real_page_size),
            ('results', data)
        ]))
