"""

"""

from pyorient import PyOrientORecordDuplicatedException

from ngpyorient.base import In, Q
from ngpyorient.match import process_filter_args
from ngpyorient.queryset import NgQuerySet, NgRawQuerySet
from ngpyorient import connections
from ngpyorient.utils import format_kwargs


class Manager(object):
    """"""

    def __init__(self, source_class):
        self.source_class = source_class
        self.filters = []  # used for origin filters
        self.filters_destination = []  # used for origin filters
        self.qs = []  # used for Q filters
        self.qes = []  # used for QE filters
        self.relation = []  # used for relations eg:in,out,both

    def filter(self, *args, **kwargs):
        """
         select from person where content

         args:
         Q(),In(),Out(),Both(),
         In('likes'),Out('likes'),Both('likes')
         kwargs:
         'in_':in
         'out_':out
         'lt': less than
         'gt': greater than
         'lte': less than or equal to
         'gte': greater than or equal to
         'ne': not equal to
         'in': matches one of list (or tuple)
         'isnull': is null
         'regex': matches supplied regex (neo4j regex format)
         'exact': exactly match string (just '=')
         'contains': contains string
         'startswith': string starts with
         'endswith': string ends with
        """

        for arg in args:
            if isinstance(arg, Q) and arg.action == "end":
                self.qes.append(arg)
            elif isinstance(arg, Q) and arg.action == "start":
                self.qs.append(arg)
            elif isinstance(arg, In):
                self.relation.append(arg)
            else:
                raise Exception("unsupported type:{},value:{}".format(type(arg), arg))

        filter_origin, filter_destination = process_filter_args(self.source_class, kwargs)
        if filter_origin:
            self.filters.append(filter_origin)
        if filter_destination:
            self.filters_destination.append(filter_destination)

        return NgQuerySet(manager=self)

    def all(self):
        """"""
        return NgQuerySet(manager=self)

    def create(self, **kwargs):
        """
        vertex:CREATE VERTEX Employee CONTENT { "name" : "Jay", "surname" : "Miner" }
        edge:CREATE EDGE FROM #10:3 TO #11:4 SET brand = 'fiat'
        :param kwargs:
        :param From: 开始节点 type:Vertex
        :param From: 结束节点 type:Vertex
        :return:
        """
        format_kwargs(kwargs)
        if "out_" in kwargs or "in_" in kwargs:
            try:
                self.out_ = kwargs.pop("out_").__str__()
                self.in_ = kwargs.pop("in_").__str__()
            except KeyError:
                raise Exception("out_ and in_ must both be provided when create edge")
            # check whether id out and in vertex exist
            sql_out = "select from {}".format(self.out_)
            sql_in = "select from {}".format(self.in_)
            result_in = connections["default"].execute(sql_in)
            result_out = connections["default"].execute(sql_out)
            if not result_in:
                raise Exception("{} does not exist".format(self.in_))
            if not result_out:
                raise Exception("{} does not exist".format(self.out_))

        self.kwargs = kwargs
        return NgQuerySet(manager=self, compiler="SQLCreateCompiler").execute()

    def raw(self, raw_query):
        return NgRawQuerySet(raw_query, manager=self)

    def create_simple(self, **kwargs):
        """create if not exist and filter if exist"""
        try:
            result = self.create(**kwargs)
        except PyOrientORecordDuplicatedException as e:
            result = self.filter(**kwargs).execute()
        return result
