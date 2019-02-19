# Create your models here.
# Initialize Registries
from pyorient.ogm.property import String, Integer, Date, DateTime, Link

from ngpyorient.ng_node import NgNode
from ngpyorient.ng_relationship import NgRelationship


class Person(NgNode):
    name = String(unique=True)
    age = Integer()
    borned = Date()
    registerd_time = DateTime()
    department = Link()

class Department(NgNode):
    id = Integer(unique=True)
    name = String(unique=True)


class Phone(NgNode):
    brand = String(unique=True, mandatory=True)
    price = Integer()


class Car(NgNode):
    name = String(unique=True, mandatory=True)


class Province(NgNode):
    name = String(unique=True)


# Create Edge Class
class Likes(NgRelationship):
    label = "likes"
    md5 = String(unique=True)


class Borned(NgRelationship):
    label = "borned"
    md5 = String(unique=True)


class Country(NgNode):
    name = String(unique=True)


class Produced(NgRelationship):
    label = "produced"
    md5 = String(unique=True)

class Have(NgRelationship):
    label = "have"
    md5 = String(unique=True)
