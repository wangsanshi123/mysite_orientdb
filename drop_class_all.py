"""
util for drop all classes
"""
import os
import django
from django.conf import settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ops_platform.settings")
django.setup()
from pyorient import PyOrientSQLParsingException
from ngpyorient.graph import NgGraph
from ngpyorient.utils import write_error, write_info
from pyorient.ogm import Config
from ngpyorient.ng_node import NgNode
from ngpyorient.ng_relationship import NgRelationship

config = Config.from_url(
    settings.DATABASES_NG["default"]["URL"],
    settings.DATABASES_NG["default"]["USER"],
    settings.DATABASES_NG["default"]["PASSWORD"],
)
graph = NgGraph(config)
NgNode.registry.pop("ngnode")
NgRelationship.registry.pop("ngrelationship")
NgNode.registry.update(NgRelationship.registry)

for value in NgNode.registry.values():
    try:
        write_info("deleting {}".format(value))
        graph.drop_class_simple(value)
    except PyOrientSQLParsingException as e:
        write_error(e)
        pass
graph.client.close()



if __name__ == '__main__':
    pass
