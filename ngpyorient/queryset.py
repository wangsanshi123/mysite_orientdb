"""

"""
from importlib import import_module
from ngpyorient import connections
from ngpyorient.base import In, Q
from ngpyorient.match import process_filter_args, process_set_args, process_raw_filter_args
from django.conf import settings

from ngpyorient.utils import write_debug, format_kwargs
import re

debug = settings.DEBUG


class NgQuerySet(object):
    """"""
    compiler_module = "ngpyorient.compilers"

    def __init__(self, sql=None, manager=None, db="default", compiler="SQLCompiler"):
        self.sql = sql
        self.db = db
        self.set_args = {}
        self.compiler = compiler
        self.manager = manager
        self.filters = []  # used for origin filters
        self.filters_destination = []  # used for  destination filters
        self.qs = []  # used for Q filters
        self.qes = []  # used for QE filters
        self.relation = []  # used for relations eg:in,out,both

    def __iter__(self):
        """do real query here"""
        self._checkTypeOfQuery()
        compiler = self.get_compiler()
        results = compiler.execute_sql()
        for result in results:
            yield result

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

        filter_origin, filter_destination = process_filter_args(self.manager.source_class, kwargs)
        if filter_origin:
            self.filters.append(filter_origin)
        if filter_destination:
            self.filters_destination.append(filter_destination)
        return self

    def get_compiler(self):

        module = import_module(self.compiler_module)
        return getattr(module, self.compiler)(self, connections[self.db])

    def update(self, **kwargs):
        """
          :param From:  used for update edge
          :param To:    used for update edge
          :param kwargs:
          :return:
        """
        format_kwargs(kwargs)
        self.set_args.update(process_set_args(self.manager.source_class, kwargs))
        self.compiler = "SQLUpdateCompiler"
        compiler = self.get_compiler()
        return compiler.execute_sql()

    def delete(self):
        """
        DELETE VERTEX #10:231
        DELETE EDGE #22:38
        :param record_id:
        :return:
        """
        self.compiler = "SQLDeleteCompiler"
        compiler = self.get_compiler()
        return compiler.execute_sql()

    def execute(self):
        """一般情况不调用此方法"""
        self._checkTypeOfQuery()
        compiler = self.get_compiler()
        result = compiler.execute_sql()
        return result

    def all(self):
        """"""
        clone = self.__class__(sql=self.sql, manager=self.manager, db=self.db, compiler=self.compiler)
        clone.qs = self.qs.copy()
        clone.qes = self.qes.copy()
        clone.relation = self.relation.copy()
        clone.filters = self.filters.copy()
        clone.filters_destination = self.filters_destination.copy()
        clone.set_args = self.set_args.copy()
        return clone

    def _checkTypeOfQuery(self):
        for item in self.relation + self.manager.relation:
            if item.action == "select":
                self.compiler = "SpanWithSelectSQLCompiler"
                if not (self.relation + self.manager.relation):
                    raise Exception("QE() query should be used with specific orientation,eg:in,out,both")
            else:
                self.compiler = "SpanWithTraverseSQLCompiler"

    def count(self):
        """
        Performs a COUNT() query using the current filter constraints.
        """
        compiler = self.get_compiler()
        compiler.query_builder.add_annotation("count(*)", alias='count')
        results = compiler.execute_sql()
        return results[0].count

    def paginate(self, skip, limit):
        self._checkTypeOfQuery()
        compiler = self.get_compiler()
        compiler.query_builder.add_skip_limit(skip=skip, limit=limit)
        results = compiler.execute_sql()
        return results


class NgRawQuerySet(NgQuerySet):
    """"""

    def __init__(self, raw_query, db="default", manager=None):
        self.raw_query = raw_query
        self.db = db
        self.manager = manager
        self.compiler = "SQLRawCompiler"

    def __iter__(self):
        self.log(self.raw_query)
        results = connections[self.db].execute(self.raw_query)
        for result in results:
            yield result

    def execute(self):
        self.log(self.raw_query)
        return connections[self.db].execute(self.raw_query)

    def log(self, sql):
        if debug:
            write_debug(sql)

    def all(self):
        clone = self.__class__(raw_query=self.raw_query, manager=self.manager, db=self.db)
        return clone

    def paginate(self, skip, limit):
        compiler = self.get_compiler()
        compiler.query_builder.add_skip_limit(skip=skip, limit=limit)
        results = compiler.execute_sql()
        return results
