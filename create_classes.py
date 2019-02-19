"""
util for create classes
"""
import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite_orientdb.settings")
django.setup()
from pyorient.ogm import Graph, Config
from ngpyorient.ng_node import NgNode
from ngpyorient.ng_relationship import NgRelationship

config = Config.from_url(
    settings.DATABASES_NG["default"]["URL"],
    settings.DATABASES_NG["default"]["USER"],
    settings.DATABASES_NG["default"]["PASSWORD"],
)
graph = Graph(config)

# NgNode.registry.pop("ngnode")
# NgRelationship.registry.pop("ngrelationship")

graph.create_all(NgNode.registry)
graph.create_all(NgRelationship.registry)
graph.client.close()
