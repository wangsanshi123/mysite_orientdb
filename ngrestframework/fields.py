"""

"""
from rest_framework.fields import DateTimeField, DateField, Field


class DateTimeField(DateTimeField):
    def to_internal_value(self, value):
        return super().to_internal_value(value)

    def to_representation(self, value):
        if not value:
            return None
        return value.strftime("%Y-%m-%d %H:%M:%S")


class DateField(DateField):
    def to_internal_value(self, value):
        return super().to_internal_value(value)

    def to_representation(self, value):
        if not value:
            return None
        return value.strftime("%Y-%m-%d")


class MethodField(Field):
    """
     这个方法放血了SerializerMethodField, 没有限制只能读取不能写入
     但是在编写get_{field_name}方法时候要注意传进去的值不是instance了, 而是结果
     如 def get_staff__rid__first(self, obj_list):
            return ",".join([str(i) for i in obj_list])
     """
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        # kwargs['source'] = '*'
        # kwargs['read_only'] = True
        super(MethodField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        # In order to enforce a consistent style, we error if a redundant
        # 'method_name' argument has been used. For example:
        # my_field = serializer.SerializerMethodField(method_name='get_my_field')
        default_method_name = 'get_{field_name}'.format(field_name=field_name)
        assert self.method_name != default_method_name, (
                "It is redundant to specify `%s` on SerializerMethodField '%s' in "
                "serializer '%s', because it is the same as the default method name. "
                "Remove the `method_name` argument." %
                (self.method_name, field_name, parent.__class__.__name__)
        )

        # The method name should default to `get_{field_name}`.
        if self.method_name is None:
            self.method_name = default_method_name
        self.field_name = field_name
        self.parent = parent
        # `self.label` should default to being based on the field name.
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()

        # self.source should default to being the same as the field name.
        if self.source is None:
            self.source = field_name
        self.source_attrs = self.source.split(".")
        # super(MethodField, self).bind(field_name, parent)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value)

    def to_internal_value(self, data):
        return data
