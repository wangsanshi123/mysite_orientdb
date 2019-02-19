"""

"""
from __future__ import unicode_literals

from django.utils import six
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import _get_error_details, _get_codes, _get_full_details
from rest_framework.response import Response
from rest_framework.views import exception_handler


def ng_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is None:
        response = ng_exception(exc, context)
        pass

    return response


def ng_exception(exc, context):
    if isinstance(exc, NgException):
        data = {"info": exc.detail, "results": {}}
        return Response(data, status=exc.status_code)
    pass


class NgException(Exception):
    """
        Base class for REST framework exceptions.
        Subclasses should provide `.status_code` and `.default_detail` properties.
        """
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail=None, code=None, status_code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        if status_code:
            self.status_code = status_code
        self.detail = _get_error_details(detail, code)

    def __str__(self):
        return six.text_type(self.detail)

    def get_codes(self):
        """
        Return only the code part of the error details.

        Eg. {"name": ["required"]}
        """
        return _get_codes(self.detail)

    def get_full_details(self):
        """
        Return both the message & code parts of the error details.

        Eg. {"name": [{"message": "This field is required.", "code": "required"}]}
        """
        return _get_full_details(self.detail)


pass
