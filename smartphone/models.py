from django.db import models
# Create your models here.
from pyorient.ogm import Config, declarative
# Initialize Registries
from pyorient.ogm.property import String, Integer

from ngpyorient.graph import NgGraph

# Create your models here.

config = Config.from_url(
    'plocal://10.60.49.214:2424/test1',
    'root',
    'rootpwd'
)

Node = declarative.declarative_node()
Relationship = declarative.declarative_relationship()
# graph = NgGraph(config)


class SmartPhone(Node):
    element_plural = "smartPhone"
    brand = String(unique=True)
    price = Integer()
