"""
utils for generating data
"""

import os

import django
from django.conf import settings

from ngpyorient.queryset import NgQuerySet
from person.models import Borned, Person, Car, Province, Likes, Have, Produced

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite_orientdb.settings")
django.setup()
from pyorient.ogm import Graph, Config

config = Config.from_url(
    settings.DATABASES_NG["default"]["URL"],
    settings.DATABASES_NG["default"]["USER"],
    settings.DATABASES_NG["default"]["PASSWORD"],
)
graph = Graph(config)


def create_vertex():
    """CREATE VERTEX Employee CONTENT { "name" : "Jay", "surname" : "Miner" }"""
    records = graph.client.command("create vertex person content{'name':'yuan1','age':1}")
    records = graph.client.command("create vertex person content{'name':'yuan2','age':1}")
    records = graph.client.command("create vertex person content{'name':'yuan3','age':1}")
    records = graph.client.command("create vertex person content{'name':'yuan4','age':1}")

    records = graph.client.command("create vertex province content{'name':'hubei'}")
    records = graph.client.command("create vertex province content{'name':'guangdong'}")

    records = graph.client.command("create vertex phone content{'brand':'samsung'}")
    records = graph.client.command("create vertex phone content{'brand':'huawei'}")
    records = graph.client.command("create vertex phone content{'brand':'xiaomi'}")
    records = graph.client.command("create vertex phone content{'brand':'vivo'}")
    records = graph.client.command("create vertex phone content{'brand':'oppo'}")
    records = graph.client.command("create vertex phone content{'brand':'apple'}")

    records = graph.client.command("create vertex car content{'name':'dazhong'}")
    records = graph.client.command("create vertex car content{'name':'benchi'}")
    records = graph.client.command("create vertex car content{'name':'aodi'}")
    records = graph.client.command("create vertex car content{'name':'Ford'}")
    records = graph.client.command("create vertex car content{'name':'BYD'}")

    records = graph.client.command("create vertex country content{'name':'Germany'}")
    records = graph.client.command("create vertex country content{'name':'USA'}")
    records = graph.client.command("create vertex country content{'name':'China'}")


def create_edges():
    """
        1 CREATE EDGE Eat FROM #11:1 TO #12:0
        2 CREATE EDGE Eat FROM ( SELECT FROM Person WHERE name='Luca' )
             TO ( SELECT FROM Restaurant WHERE name='Dante' )
       :return:
       """
    records = graph.client.command(
        "create edge borned from (select from person where name like 'y%') to (select from province where name='hubei')")

    records = graph.client.command(
        "create edge borned from (select from person where name in ['yuan1','yuan2']) to (select from province where name='hubei')")

    records = graph.client.command(
        "create edge borned from (select from person where name in ['yuan3','yuan4']) to (select from province where name='guangdong')")

    records = graph.client.command(
        "create edge relations from (select from person where name in ['yuan1','yuan3']) to (select from smartphone where brand='xiaomi')")

    records = graph.client.command(
        "create edge relations from (select from person where name in ['yuan1','yuan3']) to (select from car where name='dazhong')")

    records = graph.client.command(
        "create edge relations from (select from person where name in ['yuan1','yuan3']) to (select from car where name='aodi')")

    records = graph.client.command(
        "create edge produced from (select from car where name in ['aodi','benchi']) to (select from province where name='guangdong')")

    records = graph.client.command(
        "create edge produced from (select from car where name in ['aodi','dazhong']) to (select from province where name='hubei')")


def create_edges_with_md5():
    """"""
    # borned in province
    Borned.objects.create(out_="#106:0", in_="#202:0")
    Borned.objects.create(out_="#107:0", in_="#203:0")

    # like phone
    Likes.objects.create(out_="#106:0", in_="#138:0")
    Likes.objects.create(out_="#106:0", in_="#139:0")
    Likes.objects.create(out_="#106:0", in_="#140:0")
    Likes.objects.create(out_="#106:0", in_="#141:0")
    Likes.objects.create(out_="#106:0", in_="#142:0")
    Likes.objects.create(out_="#107:0", in_="#139:0")
    Likes.objects.create(out_="#107:0", in_="#140:0")
    Likes.objects.create(out_="#107:0", in_="#141:0")
    Likes.objects.create(out_="#107:0", in_="#142:0")

    # like car
    Likes.objects.create(out_="#106:0", in_="#170:0")
    Likes.objects.create(out_="#106:0", in_="#171:0")
    Likes.objects.create(out_="#107:0", in_="#171:0")

    Likes.objects.create(out_="#106:0", in_="#172:0")
    Likes.objects.create(out_="#106:0", in_="#173:0")
    Likes.objects.create(out_="#106:0", in_="#174:0")
    Likes.objects.create(out_="#107:0", in_="#172:0")
    Likes.objects.create(out_="#107:0", in_="#173:0")
    Likes.objects.create(out_="#108:0", in_="#173:0")

    # country have car
    Have.objects.create(out_="#266:0", in_="#170:0")
    Have.objects.create(out_="#266:0", in_="#171:0")
    Have.objects.create(out_="#266:0", in_="#172:0")
    Have.objects.create(out_="#267:0", in_="#173:0")
    Have.objects.create(out_="#268:0", in_="#174:0")

    # phone produce in province
    Produced.objects.create(out_="#138:0", in_="#202:0")
    Produced.objects.create(out_="#138:0", in_="#203:0")
    Produced.objects.create(out_="#139:0", in_="#202:0")
    Produced.objects.create(out_="#139:0", in_="#203:0")
    Produced.objects.create(out_="#140:0", in_="#202:0")
    Produced.objects.create(out_="#141:0", in_="#202:0")
    Produced.objects.create(out_="#142:0", in_="#202:0")
    Produced.objects.create(out_="#143:0", in_="#203:0")


if __name__ == '__main__':
    """"""
    # create_vertex()
    # create_edges_with_md5()
    # country have car

    # country have car

    # borned in province
    # Borned.objects.create(out_="#106:0", in_="#203:0")
    Likes.objects.create(out_="#106:0", in_="#172:0")
    Likes.objects.create(out_="#106:0", in_="#173:0")
    Likes.objects.create(out_="#106:0", in_="#174:0")
    Likes.objects.create(out_="#107:0", in_="#172:0")
    Likes.objects.create(out_="#107:0", in_="#173:0")
    Likes.objects.create(out_="#108:0", in_="#173:0")