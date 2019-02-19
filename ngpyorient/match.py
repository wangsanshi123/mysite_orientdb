"""

"""

# special operators
import re

_SPECIAL_OPERATOR_IN = "IN"
_SPECIAL_OPERATOR_INSENSITIVE = "(?i)"
_SPECIAL_OPERATOR_ISNULL = "IS NULL"
_SPECIAL_OPERATOR_ISNOTNULL = "IS NOT NULL"
_SPECIAL_OPERATOR_REGEX = "like"

_UNARY_OPERATORS = (_SPECIAL_OPERATOR_ISNULL, _SPECIAL_OPERATOR_ISNOTNULL)

_REGEX_INSESITIVE = _SPECIAL_OPERATOR_INSENSITIVE + "{}"
_REGEX_CONTAINS = "%{}%"
_REGEX_STARTSWITH = "{}%"
_REGEX_ENDSWITH = "%{}"

# regex operations that require escaping
_STRING_REGEX_OPERATOR_TABLE = {
    "iexact": _REGEX_INSESITIVE,
    "contains": _REGEX_CONTAINS,
    "icontains": _SPECIAL_OPERATOR_INSENSITIVE + _REGEX_CONTAINS,
    "startswith": _REGEX_STARTSWITH,
    "istartswith": _SPECIAL_OPERATOR_INSENSITIVE + _REGEX_STARTSWITH,
    "endswith": _REGEX_ENDSWITH,
    "iendswith": _SPECIAL_OPERATOR_INSENSITIVE + _REGEX_ENDSWITH,
}
# regex operations that do not require escaping
_REGEX_OPERATOR_TABLE = {
    "iregex": _REGEX_INSESITIVE,
}
# list all regex operations, these will require formatting of the value
_REGEX_OPERATOR_TABLE.update(_STRING_REGEX_OPERATOR_TABLE)

# list all supported operators
OPERATOR_TABLE = {
    "lt": "<",
    "gt": ">",
    "lte": "<=",
    "gte": ">=",
    "ne": "<>",
    "in": _SPECIAL_OPERATOR_IN,
    "isnull": _SPECIAL_OPERATOR_ISNULL,
    "regex": _SPECIAL_OPERATOR_REGEX,
    "exact": "="
}
# add all regex operators
OPERATOR_TABLE.update(_REGEX_OPERATOR_TABLE)
DEFAULT_FILTER_TERMS = ["rid", "class"]
CUSTOM_FILTER_TERMS = ["out_", "in_", "out", "in"]
IDS = ["rid", "in", "out"]
FILTER_KEYWORDS = list(OPERATOR_TABLE.keys()) + list(
    _STRING_REGEX_OPERATOR_TABLE.keys())  # keywords that should not be property of class


def process_filter_args(cls, kwargs):
    filter_origin = {}  # used to filter origin vertex
    filter_destination = {}  # used to filter destination vertex

    for key, value in kwargs.items():
        """
        key = name__startswith
        key = car__name
        key = car__name__startswith
        
        """
        class_name = None
        if key in CUSTOM_FILTER_TERMS:
            key = key.split("_")[0]
        if "__" in key:
            # filter origin eg:key = name__startswith
            if key.rsplit("__")[1] in FILTER_KEYWORDS:
                prop, operator = key.rsplit("__")
                operator = OPERATOR_TABLE[operator]
            # filter destination eg:key = car__name__startswith
            elif len(key.rsplit("__")) > 2:
                class_name, prop, operator = key.rsplit("__")
                operator = OPERATOR_TABLE[operator]
            # filter destination eg:key = car__name
            else:
                class_name, prop = key.rsplit("__")
                operator = "="
        else:
            prop = key
            operator = "="

        if prop not in (defined_properties(cls) + DEFAULT_FILTER_TERMS + CUSTOM_FILTER_TERMS) and not class_name:
            raise ValueError("No such property {} on {}".format(prop, cls.__name__))

        # handle special operators
        if operator == _SPECIAL_OPERATOR_IN:
            if not isinstance(value, tuple) and not isinstance(value, list):
                raise ValueError("Value must be a tuple or list for IN operation {}={}".format(key, value))
            # deflated_value = [property_obj.deflate(v) for v in value]
            deflated_value = [v for v in value]
        elif operator == _SPECIAL_OPERATOR_ISNULL:
            if not isinstance(value, bool):
                raise ValueError("Value must be a bool for isnull operation on {}".format(key))
            operator = "IS NULL" if value else "IS NOT NULL"
            deflated_value = None
        elif operator in _REGEX_OPERATOR_TABLE.values():
            deflated_value = value
            if not isinstance(deflated_value, str):
                raise ValueError("Must be a string value for {}".format(key))
            deflated_value = operator.format(deflated_value)
            operator = _SPECIAL_OPERATOR_REGEX
        else:
            deflated_value = value
        # map property to correct property name in the database
        # db_property = cls.defined_properties(rels=False)[prop].db_property or prop
        db_property = prop.split("_")[0] if prop in ["in_", "out_"] else prop
        if class_name:
            filter_destination[db_property] = (operator, deflated_value, class_name)
        else:
            filter_origin[db_property] = (operator, deflated_value)
    return filter_origin, filter_destination


def process_set_args(cls, kwargs):
    """check the properties when update"""
    for key, value in kwargs.copy().items():
        if key in CUSTOM_FILTER_TERMS:
            kwargs.pop(key)
            key = key.split("_")[0]
            kwargs[key] = value
        if key not in (defined_properties(cls) + CUSTOM_FILTER_TERMS):
            raise ValueError("No such property {} on {}".format(key, cls.__name__))
    return kwargs


def process_q_args(cls, qs):
    """"""
    ls = [[item.connector, [list(i) for i in item.children]] for item in qs]
    for item in ls:
        connector, expressons = item
        for item_ in expressons:
            key, value = item_
            if "__" in key:
                prop, operator = key.rsplit("__")
                try:
                    operator = OPERATOR_TABLE[operator]
                except KeyError:
                    raise Exception(
                        "operator {} is not supported operator,maybe you should user QE() instead of Q()".format(
                            operator))
                    pass
            else:
                prop = key
                operator = "="
            # todo: 这个地方, 传入进去的筛选字段不一定是在以下列出的里面
            # if prop not in (defined_properties(cls) + DEFAULT_FILTER_TERMS + CUSTOM_FILTER_TERMS):
            #     raise ValueError("No such property {} on {}".format(prop, cls.__name__))

            # handle special operators
            if operator == _SPECIAL_OPERATOR_IN:
                if not isinstance(value, tuple) and not isinstance(value, list):
                    raise ValueError("Value must be a tuple or list for IN operation {}={}".format(key, value))
                # deflated_value = [property_obj.deflate(v) for v in value]
                deflated_value = [v for v in value]
            elif operator == _SPECIAL_OPERATOR_ISNULL:
                if not isinstance(value, bool):
                    raise ValueError("Value must be a bool for isnull operation on {}".format(key))
                operator = "IS NULL" if value else "IS NOT NULL"
                deflated_value = None
            elif operator in _REGEX_OPERATOR_TABLE.values():
                deflated_value = value
                if not isinstance(deflated_value, str):
                    raise ValueError("Must be a string value for {}".format(key))
                if operator in _STRING_REGEX_OPERATOR_TABLE.values():
                    deflated_value = re.escape(deflated_value)
                deflated_value = operator.format(deflated_value)
                operator = _SPECIAL_OPERATOR_REGEX
            else:
                deflated_value = value
            # map property to correct property name in the database
            # db_property = cls.defined_properties(rels=False)[prop].db_property or prop
            db_property = prop
            item_[0], item_[1] = db_property, operator
            item_.append(deflated_value)
    return ls


def process_qe_args(cls, qs):
    """"""
    ls = [[item.connector, [list(i) for i in item.children]] for item in qs]
    for item in ls:
        connector, expressons = item
        for item_ in expressons:
            key, value = item_
            if "__" in key:
                # filter origin eg:key = name__startswith
                if key.rsplit("__")[1] in FILTER_KEYWORDS:
                    raise Exception(
                        "QE only filter the end ,{} is not the right format,eg:car__name,person__age__gte".format(key))
                # filter destination eg:key = car__name__startswith
                elif len(key.rsplit("__")) > 2:
                    class_name, prop, operator = key.rsplit("__")
                    operator = OPERATOR_TABLE[operator]
                # filter destination eg:key = car__name
                else:
                    class_name, prop = key.rsplit("__")
                    operator = "="
            else:
                raise Exception(
                    "QE only filter the end ,{} is not the right format,eg:car__name,person__age__gte".format(key))

            # handle special operators
            if operator == _SPECIAL_OPERATOR_IN:
                if not isinstance(value, tuple) and not isinstance(value, list):
                    raise ValueError("Value must be a tuple or list for IN operation {}={}".format(key, value))
                deflated_value = [v for v in value]
            elif operator == _SPECIAL_OPERATOR_ISNULL:
                if not isinstance(value, bool):
                    raise ValueError("Value must be a bool for isnull operation on {}".format(key))
                operator = "IS NULL" if value else "IS NOT NULL"
                deflated_value = None
            elif operator in _REGEX_OPERATOR_TABLE.values():
                deflated_value = value
                if not isinstance(deflated_value, str):
                    raise ValueError("Must be a string value for {}".format(key))
                if operator in _STRING_REGEX_OPERATOR_TABLE.values():
                    deflated_value = re.escape(deflated_value)
                deflated_value = operator.format(deflated_value)
                operator = _SPECIAL_OPERATOR_REGEX
            else:
                deflated_value = value
            db_property = prop
            item_[0], item_[1] = db_property, operator
            item_.append(deflated_value)
            item_.append(class_name)
    return ls


def check_create_args(cls, kwargs):
    """check the properties when create vertex"""
    for key, value in kwargs.items():
        if key not in defined_properties(cls):
            raise ValueError("No such property: '{}' on {}".format(key, cls.__name__))


def defined_properties(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != "_"]


###############################raw sql match##############################################################################


def process_raw_filter_args(cls, kwargs):
    """prcess filters in raw sql"""
    filters = {}
    for key, value in kwargs.items():
        """
        key = name__contains
        """
        if "__" in key:
            if len(key.rsplit("__")) >= 3:
                operator = key.rsplit("__")[-1]
                prop = key.replace("__" + operator, "")
                if operator.lower() != "contains":
                    raise Exception("{} is unsupported operation,only support contains".format(operator))
                operator = "containstext"
            else:
                prop = key
                operator = "contains"

        else:
            raise Exception("method filter_result only support filter related node ,if you want to filter"
                            "the current node,you should use in raw sql now.In the future,there will be a "
                            "filter method to cover this demand")

        filters[prop] = (operator, value)
    return filters


def process_raw_q_args(cls, qs):
    """prcess q filters in raw sql"""
    ls = [[item.connector, [list(i) for i in item.children]] for item in qs]
    for item in ls:
        connector, expressons = item
        for item_ in expressons:
            key, value = item_
            if "__" in key:
                if len(key.rsplit("__")) >= 3:
                    operator = key.rsplit("__")[-1]
                    prop = key.rstrip("__" + operator)
                    if operator.lower() != "contains":
                        raise Exception("{} is unsupported operation,only support contains".format(operator))
                    operator = "containstext"
                else:
                    prop = key
                    operator = "contains"

            else:
                raise Exception("method filter_result only support filter related node ,if you want to filter"
                                "the current node,you should use in raw sql now.In the future,there will be a "
                                "filter method to cover this demand")
            # handle special operators
            if operator == _SPECIAL_OPERATOR_IN:
                if not isinstance(value, tuple) and not isinstance(value, list):
                    raise ValueError("Value must be a tuple or list for IN operation {}={}".format(key, value))
                # deflated_value = [property_obj.deflate(v) for v in value]
                deflated_value = [v for v in value]
            elif operator == _SPECIAL_OPERATOR_ISNULL:
                if not isinstance(value, bool):
                    raise ValueError("Value must be a bool for isnull operation on {}".format(key))
                operator = "IS NULL" if value else "IS NOT NULL"
                deflated_value = None
            elif operator in _REGEX_OPERATOR_TABLE.values():
                deflated_value = value
                if not isinstance(deflated_value, str):
                    raise ValueError("Must be a string value for {}".format(key))
                if operator in _STRING_REGEX_OPERATOR_TABLE.values():
                    deflated_value = re.escape(deflated_value)
                deflated_value = operator.format(deflated_value)
                operator = _SPECIAL_OPERATOR_REGEX
            else:
                deflated_value = value
            # map property to correct property name in the database
            # db_property = cls.defined_properties(rels=False)[prop].db_property or prop
            db_property = prop
            item_[0], item_[1] = db_property, operator
            item_.append(deflated_value)
    return ls
