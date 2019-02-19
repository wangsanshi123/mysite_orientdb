"""

"""
import logging

from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone
from pandas import DataFrame
from rest_framework import serializers
from rest_framework.serializers import Serializer

logger = logging.getLogger('django')


class NgSerializerWithRid(Serializer):
    """list should extend this serializer"""
    _rid = serializers.CharField(help_text='rid', required=False)


class ListAddId(Serializer):
    """添加id字段"""
    rid = serializers.SerializerMethodField(help_text="id")

    def get_rid(self, obj):
        return obj._rid


class ExtraSerializer:
    """自动添加一些共同的字段信息, 也是再继承使用"""

    def extra_create(self, validated_data, model_name=None, name=None):
        user = self.context['request'].user
        if isinstance(user, AnonymousUser):
            username = 'AnonymousUser'
        else:
            username = user.alias if user.alias else user.username
        now = str(timezone.now())
        save_data = dict([(key, value) for key, value in validated_data.items()])
        save_data.update({'founder': username, 'updater': username, 'create_time': now, 'update_time': now})
        logger.info(u'用户%s创建名称是%s的%s成功' % (username, name, model_name))
        return save_data

    def extra_update(self, validated_data, model_name=None, name=None):
        user = self.context['request'].user
        if isinstance(user, AnonymousUser):
            username = 'AnonymousUser'
        else:
            username = user.alias if user.alias else user.username
        now = str(timezone.now())
        update_data = dict([(key, value) for key, value in validated_data.items()])
        update_data.update({'updater': username, 'update_time': now})
        logger.info(u'用户%s更新名称是%s的%s成功' % (username, name, model_name))
        return update_data


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
            return self.context['view'].transform_dataframe(dataframe)
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
