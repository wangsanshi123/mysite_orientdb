"""

"""
from pyorient import PyOrientORecordDuplicatedException
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from ngpyorient.exceptions import DuplicateError
from person.models import Person


class PersonSerializer(serializers.Serializer):
    """"""
    # _rid = serializers.CharField(max_length=10, required=False)
    name = serializers.CharField(max_length=5)
    age = serializers.IntegerField(required=False)
    borned = serializers.DateField(allow_null=True, required=False)

    def create(self, validated_data):
        """INSERT INTO Profile CONTENT {"name": "Jay", "surname": "Miner"}"""
        Person.objects.create(**validated_data)
        return validated_data

    def update(self, kwargs, validated_data):
        try:
            result = Person.objects.filter(**kwargs).update(**validated_data)
        except PyOrientORecordDuplicatedException as e:
            raise DuplicateError("该姓名已经存在")
        if not result[0]:
            raise NotFound()
        return validated_data
