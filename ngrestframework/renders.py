import json
import os
from io import StringIO
from tempfile import mkstemp

from pandas import DataFrame
from rest_framework import status
from rest_framework.renderers import BaseRenderer, JSONRenderer
from rest_framework.status import is_success

from ngpyorient.queryset import NgRawQuerySet
from ngrestframework.utils import format_data, convert, format_data_new
import pandas as pd

RESPONSE_ERROR = (
    "Response data is a %s, not a DataFrame! "
    "Did you extend PandasMixin?"
)


class PandasBaseRenderer(BaseRenderer):
    """
    Renders DataFrames using their built in pandas implementation.
    Only works with serializers that return DataFrames as their data object.
    Uses a StringIO to capture the output of dataframe.to_[format]()
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'response' in renderer_context:
            status_code = renderer_context['response'].status_code
            if not status.is_success(status_code):
                return "Error: %s" % data.get('detail', status_code)

        if not isinstance(data, DataFrame):
            raise Exception(
                RESPONSE_ERROR % type(data).__name__
            )

        name = getattr(self, 'function', "to_%s" % self.format)
        if not hasattr(data, name):
            raise Exception("Data frame is missing %s property!" % name)

        self.init_output()
        args = self.get_pandas_args(data)
        kwargs = self.get_pandas_kwargs(data, renderer_context)
        self.render_dataframe(data, name, *args, **kwargs)
        return self.get_output()

    def render_dataframe(self, data, name, *args, **kwargs):
        function = getattr(data, name)
        function(*args, **kwargs)

    def init_output(self):
        self.output = StringIO()

    def get_output(self):
        return self.output.getvalue()

    def get_pandas_args(self, data):
        return [self.output]

    def get_pandas_kwargs(self, data, renderer_context):
        return {}


class PandasJSONRenderer(PandasBaseRenderer):
    """
    Renders data frame as JSON
    """
    media_type = "application/json"
    format = "json"

    orient_choices = {
        'records-index',  # Unique to DRP
        'split',
        'records',
        'index',
        'columns',
        'values',
        'table',
    }
    default_orient = 'records-index'

    date_format_choices = {'epoch', 'iso'}
    default_date_format = 'iso'

    def get_pandas_kwargs(self, data, renderer_context):
        request = renderer_context['request']

        orient = request.GET.get('orient', '')
        if orient not in self.orient_choices:
            orient = self.default_orient

        date_format = request.GET.get('date_format', '')
        if date_format not in self.date_format_choices:
            date_format = self.default_date_format

        return {
            'orient': orient,
            'date_format': date_format,
        }

    def render_dataframe(self, data, name, *args, **kwargs):
        if kwargs.get('orient') == 'records-index':
            kwargs['orient'] = 'records'
            data.reset_index(inplace=True)
        return super(PandasJSONRenderer, self).render_dataframe(
            data, name, *args, **kwargs
        )


class NgRender_deprecated(PandasJSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        queryset = renderer_context["view"].get_queryset()
        queryset = renderer_context["view"].filter_queryset(queryset)

        if isinstance(queryset, NgRawQuerySet) and is_success(renderer_context["response"].status_code) \
                and renderer_context["view"].action in ["list", "retrieve"]:
            result = format_data(data, queryset)
            # result = format_data_new(data, queryset)
            temp = super().render(result, accepted_media_type, renderer_context)
            # data = convert(data)
        compose_data = {"info": "", "results": {"lists": json.loads(temp)}}
        return json.dumps(compose_data)


class NgRender(JSONRenderer):
    charset = "utf8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        action = renderer_context["view"].action
        status = renderer_context["response"].status_code
        json_binary_data = super().render(data, accepted_media_type, renderer_context)
        if action == "list":
            if not json_binary_data:
                composed_data = {"info": "", "results": {"lists": None}}
            else:
                raw_data = json.loads(json_binary_data)
                if isinstance(raw_data, dict) and "results" in raw_data:
                    composed_data = {"info": "", 'results': {"lists": raw_data.pop('results'), "pagination": raw_data}}
                else:
                    composed_data = {"info": "", "results": {"lists": raw_data}}
        elif action in ['create', 'update', 'destroy'] and is_success(status):
            # 根据返回的结果进行定义
            composed_data = {
                "info": "操作成功", "results": json.loads(json_binary_data)} if json_binary_data and len(
                json_binary_data) > 2 else {
                "info": "操作成功", "results": {}}
        elif action in ['retrieve']:
            # 根据返回的结果进行定义
            composed_data = {
                "info": "", "results": {"lists": json.loads(json_binary_data)}} if json_binary_data and len(
                json_binary_data) > 2 else {
                "info": "", "results": {}}
        else:
            composed_data = data if data else {"info": "", "results": {}}

        return json.dumps(composed_data)
