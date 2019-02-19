"""

"""
import logging

# logging.basicConfig函数对日志的输出格式及方式做相关配置
import pytz
from django.db.models import Q
import datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s: %(message)s')


def classproperty(f):
    class cpf(object):
        def __init__(self, getter):
            self.getter = getter

        def __get__(self, obj, type=None):
            return self.getter(type)

    return cpf(f)


def write_warning(msg):
    logging.warning(msg)


def write_error(msg):
    logging.error(msg)


def write_info(msg):
    logging.info(msg)


def write_debug(msg):
    logging.debug(msg)


def format_kwargs(kwargs):
    for key, value in kwargs.copy().items():
        if type(value) == datetime.datetime:
            kwargs[key] = value.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M:%S")
        elif type(value) == datetime.date:
            kwargs[key] = value.strftime("%Y-%m-%d")
    pass