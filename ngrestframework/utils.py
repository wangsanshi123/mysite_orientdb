"""

"""
import pandas as pd
import numpy as np
from numpy import NaN

from ngpyorient.queryset import NgRawQuerySet


def format_data(data, queryset):
    """
    convert data to dataFrame to unpack the list result of sql
    :param data:
    :return:
    """
    df_default = pd.DataFrame()
    for item in data:
        data_end = {}  # data for end vertex
        data_start = {}  # data for start vertex
        for key, value in item.items():
            if type(value) == list:
                if len(key.split("__")) == 1:
                    raise Exception(
                        "{} is unsupport format,when filter end,you should use like this:car__name".format(key))
                # class_name, property = key.split("__")
                class_name = key.split("__")[0]
                # property = key.split("__")[1:]
                if len(key.split("__")) > 2:
                    class_name = key.split("__")[0] + "".join(key.split("__")[2:])
                if class_name not in data_end:
                    data_end[class_name] = {}
                data_end[class_name].update({key: value})
            else:
                data_start.update({key: value})
        df_end_item = pd.DataFrame()  # store end vertexs(used to join vertex together)

        for key, value in data_end.items():
            # add  end vertex
            df = pd.DataFrame(value)
            # add start vertex
            for key, value in data_start.items():
                df[key] = value

            if not df_end_item.empty:
                df_end_item = pd.merge(df_end_item, df, how='outer')
            else:
                df_end_item = df
        if not df_default.empty:
            df_default = df_default.append(df_end_item)
        else:
            df_default = df_end_item
    df_default = df_default.reset_index()

    # filter queryset
    df_default = filter_result(df_default, queryset)
    # category properties by class_name
    # df_default.columns = pd.MultiIndex.from_tuples(
    #     [split_class_and_property(column, queryset.manager.source_class.__name__) for column in df_default.columns])
    temp = df_default.groupby(['rid','host_name']).agg(lambda x: ', '.join(x)).reset_index()
    # return df_default
    return temp


def split_class_and_property(column, source_class):
    length = len(column.split("__"))
    if length == 2:
        return tuple(column.split("__"))
    if length == 3:
        return column.split("__")[0] + "_" + column.split("__")[2], column.split("__")[1]
    if length == 1:
        return "current__{}".format(source_class), column


def convert(df):
    """convert flat dataframe to nested dataframe categoried by classname"""
    values = [value for value in df.T.to_dict().values()]
    result = []
    for item in values:
        class_dict = {}
        for key, value in item.items():
            class_name, property_name = key
            key = class_name
            # convert nan to None
            if value is NaN:
                value = None

            if key in class_dict:
                class_dict[key].update({property_name: value})
            else:
                class_dict.update({key: {property_name: value}})
        result.append(class_dict)
    return result


def filter_result(result, queryset):
    """
    :param result:dataframe
    :param queryset:
    :return: dataframe
    """
    if isinstance(queryset, NgRawQuerySet) and queryset.filter_strs:
        return result.query(queryset.filter_strs)
    else:
        return result
def format_data_new(data, queryset):
    df = pd.DataFrame(data)
    pass