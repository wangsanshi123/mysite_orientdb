"""

"""
import logging

import pytz
from pandas import DataFrame
from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject
from rest_framework.serializers import Serializer
from pyorient.otypes import OrientRecord

from utils.common import get_username

logger = logging.getLogger('django')

from collections import OrderedDict

from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone


class NgSerializerWithRid(Serializer):
    """list should extend this serializer"""
    _rid = serializers.CharField(help_text='rid', required=False)


class ListAddId(Serializer):
    """添加id字段"""
    rid = serializers.SerializerMethodField(help_text="id")

    def get_rid(self, obj):
        return obj._rid


class ExtraSerializer:
    """自动添加一些共同的字段信息, 或者一些方法,再继承使用"""

    def batch_none_value_filter(self, validated_data, rids):
        # info:判断是批量修改的情况
        if (isinstance(rids, str) and rids.count(",")) or (isinstance(rids, (tuple, list)) and len(rids) > 1):
            for k in validated_data:
                if validated_data[k] is None or validated_data[k] == "":
                    validated_data.pop(k)

    def extra_create(self, validated_data, model_name=None, name=None):
        username = get_username(self.context['request'].user)
        # 转换时间为utc时间
        now = timezone.now().astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        save_data = dict([(key, value) for key, value in validated_data.items()])
        save_data.update({'founder': username, 'updater': username, 'create_time': now, 'update_time': now})
        logger.info(u'用户%s创建名称是%s的%s成功' % (username, name, model_name))
        return save_data

    def extra_update(self, validated_data, model_name=None, name=None):
        username = get_username(self.context['request'].user)
        # 转换时间为utc时间
        now = timezone.now().astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        # info:这一步的目的为了不改变传入的数据结构
        update_data = dict([(key, value) for key, value in validated_data.items()])
        update_data.update({'updater': username, 'update_time': now})
        logger.info(u'用户%s更新名称是%s的%s成功' % (username, name, model_name))
        return update_data

    def extra_update_str(self, old_instance, validated_data):
        update_str_list = []
        if isinstance(old_instance, OrientRecord):
            old_data = old_instance.oRecordData
            [update_str_list.append("%s由%s修改为%s" % (data, old_data[data], validated_data[data])) for data in
             validated_data if validated_data[data] != old_data[data]]

        return ", ".join(update_str_list)


class NgSerializer(Serializer):
    """serializer with splited validated_data by node"""

    def save(self, **kwargs):
        assert not hasattr(self, 'save_object'), (
                'Serializer `%s.%s` has old-style version 2 `.save_object()` '
                'that is no longer compatible with REST framework 3. '
                'Use the new-style `.create()` and `.update()` methods instead.' %
                (self.__class__.__module__, self.__class__.__name__)
        )

        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.save()`.'
        )

        assert not self.errors, (
            'You cannot call `.save()` on a serializer with invalid data.'
        )

        # Guard against incorrect use of `serializer.save(commit=False)`
        assert 'commit' not in kwargs, (
            "'commit' is not a valid keyword argument to the 'save()' method. "
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
            "You can also pass additional keyword arguments to 'save()' if you "
            "need to set extra attributes on the saved model instance. "
            "For example: 'serializer.save(owner=request.user)'.'"
        )

        assert not hasattr(self, '_data'), (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = dict(
            list(self.validated_data.items()) +
            list(kwargs.items())
        )
        origin_validated_data = validated_data
        validated_data = self._split_valicated_data(validated_data)
        if self.instance is not None:
            self.instance = self.update(self.instance, validated_data, origin_validated_data)
            assert self.instance is not None, (
                '`update()` did not return an object instance.'
            )
        else:
            self.instance = self.create(validated_data, origin_validated_data)
            assert self.instance is not None, (
                '`create()` did not return an object instance.'
            )

        return self.instance

    def update(self, instance, validated_data, origin_validated_data):

        pass

    def create(self, validated_data, origin_validated_data):
        pass

    def _split_valicated_data(self, validated_data):
        """"""
        data = {}
        current = {}
        for key, value in validated_data.items():
            if "rid" in key:
                data.update({key: value})
            elif "__" in key:
                split_result = key.split("__")
                if len(split_result) == 3:
                    kclass = split_result[0] + split_result[2]
                    prop = split_result[1]
                elif len(split_result) == 2:
                    kclass, prop = split_result
                else:
                    raise Exception("{} is unsupported field".format(key))
                if kclass in data:
                    data[kclass].update({prop: value})
                else:
                    data.update({kclass: {prop: value}})
            else:
                current.update({key: value})
        data.update({"current": current})
        return data

    def to_representation(self, instance):
        """
           Object instance -> Dict of primitive datatypes.
           """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # KEY IS HERE:
            if attribute in [None]:
                attribute = ""

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class PandasSerializer(serializers.ListSerializer):
    """
    Transforms dataset into a dataframe and applies an index
    """
    read_only = True
    index_none_value = None
    wq_chart_type = None

    def get_index(self, dataframe):
        return self.get_index_fields()

    def get_dataframe(self, data):
        dataframe = DataFrame(data)
        index = self.get_index(dataframe)
        if index:
            if self.index_none_value is not None:
                for key in index:
                    try:
                        dataframe[key].fillna(
                            self.index_none_value, inplace=True
                        )
                    except ValueError:
                        pass
            dataframe.set_index(index, inplace=True)
        else:
            # Name auto-index column to ensure valid CSV output
            dataframe.index.name = 'row'
        return dataframe

    def transform_dataframe(self, dataframe):
        view = self.context.get('view', None)
        if view and hasattr(view, 'transform_dataframe'):
            return self.context['view'].stat_cost(dataframe)
        return dataframe

    @property
    def data(self):
        data = super(serializers.ListSerializer, self).data
        if isinstance(data, DataFrame) or data:
            dataframe = self.get_dataframe(data)
            return self.transform_dataframe(dataframe)
        else:
            return DataFrame([])

    def to_representation(self, data):
        if isinstance(data, DataFrame):
            return data
        return super(PandasSerializer, self).to_representation(data)

    @property
    def model_serializer(self):
        serializer = type(self.child)
        if serializer.__name__ == 'SerializerWithListSerializer':
            return serializer.__bases__[0]
        return serializer

    @property
    def model_serializer_meta(self):
        return getattr(self.model_serializer, 'Meta', object())

    def get_index_fields(self):
        """
        List of fields to use for index
        """
        index_fields = self.get_meta_option('index', [])
        if index_fields:
            return index_fields

        model = getattr(self.model_serializer_meta, 'model', None)
        if model:
            pk_name = model._meta.pk.name
            if pk_name in self.child.get_fields():
                return [pk_name]

        return []

    def get_meta_option(self, name, default=None):
        meta_name = 'pandas_' + name
        value = getattr(self.model_serializer_meta, meta_name, None)

        if value is None:
            if default is not None:
                return default
            else:
                raise ImproperlyConfigured(
                    "%s should be specified on %s.Meta" %
                    (meta_name, self.model_serializer.__name__)
                )
        return value
