"""

"""
from pyorient import PyOrientCommandException
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from ngpyorient.ng_relationship import NgRelationship


class RelationshipsSerializer(serializers.Serializer):
    """"""
    _rid = serializers.CharField(max_length=10, required=False)
    _out = serializers.CharField(max_length=10, required=False)
    _in = serializers.CharField(max_length=10, required=False)


class RelationshipsCreateSerializer(serializers.Serializer):
    """"""
    relationship_class = serializers.CharField(required=True, help_text="所建关系")
    From = serializers.CharField(required=True, help_text="起点id")
    To = serializers.CharField(required=True, help_text="终点id")

    def create(self, validated_data):
        ""
        relation = validated_data.pop("relationship_class")
        try:
            NgRelationship.registry[relation].objects.create(**validated_data)
        except PyOrientCommandException as e:
            raise NotFound()
            pass
        return validated_data
