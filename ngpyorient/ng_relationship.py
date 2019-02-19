"""

"""
from pyorient.ogm.property import String

from ngpyorient import Relationship
from ngpyorient.manager import Manager
from ngpyorient.utils import classproperty


class NgRelationship(Relationship):
    """"""
    md5 = String(unique=True)

    @classproperty
    def objects(cls):
        """

        """
        return Manager(cls)
