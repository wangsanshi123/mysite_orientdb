"""

"""
import sys

"""
util for drop specific classe
"""
import os

import django
from django.conf import settings
from pyorient import PyOrientSQLParsingException

from ngpyorient.graph import NgGraph
from ngpyorient.utils import write_error

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite_orientdb.settings")
django.setup()
from pyorient.ogm import Config

config = Config.from_url(
    settings.DATABASES_NG["default"]["URL"],
    settings.DATABASES_NG["default"]["USER"],
    settings.DATABASES_NG["default"]["PASSWORD"],
)
graph = NgGraph(config)

try:
    graph.drop_class_simple_by_class_name(sys.argv[1], sys.argv[2])
except PyOrientSQLParsingException as e:
    write_error(e)
except IndexError as e:
    write_error("you should specify classname and type(vertex or edge)")
graph.client.close()
