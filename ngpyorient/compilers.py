"""

"""
from ngpyorient.utils import write_debug
from ngpyorient.querybuilder import QueryBuilder, CreateQueryBuilder, DeleteQueryBuilder, UpdateQueryBuilder, \
    SpanWithSelectQueryBuilder, SpanWithTraverseQueryBuilder, RawQueryBuilder
from django.conf import settings
import re

debug = settings.DEBUG
try:
    test = settings.DATABASES_NG["default"]["test"]
except:
    test = False
    pass


class SQLCompiler(object):
    def __init__(self, queryset, connection):
        self.queryset = queryset
        self.connection = connection
        self.query_builder = QueryBuilder(self.queryset)

    def execute_sql(self):
        sql = self.query_builder.build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result

    def log(self, sql):
        if debug:
            write_debug(sql)


class SQLCreateCompiler(SQLCompiler):

    def execute_sql(self):
        sql = CreateQueryBuilder(self.queryset).build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result


class SQLDeleteCompiler(SQLCompiler):
    def execute_sql(self):
        sql = DeleteQueryBuilder(self.queryset).build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result


class SQLUpdateCompiler(SQLCompiler):
    def execute_sql(self):
        # return self.connection.update_records_with_transaction(self.queryset)
        sql = UpdateQueryBuilder(self.queryset).build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result


class SQLRawCompiler(SQLCompiler):
    """compile raw sql"""

    def __init__(self, queryset, connection):
        super().__init__(queryset, connection)
        self.query_builder = RawQueryBuilder(self.queryset)

    def execute_sql(self):
        sql = self.query_builder.build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result


class SpanWithSelectSQLCompiler(SQLCompiler):
    def __init__(self, queryset, connection):
        super().__init__(queryset, connection)
        self.query_builder = SpanWithSelectQueryBuilder(self.queryset)

    def execute_sql(self):
        sql = self.query_builder.build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result


class SpanWithTraverseSQLCompiler(SQLCompiler):
    def __init__(self, queryset, connection):
        super().__init__(queryset, connection)
        self.query_builder = SpanWithSelectQueryBuilder(self.queryset)

    def execute_sql(self):
        sql = self.query_builder.build_query()
        self.log(sql)
        result = sql if test else self.connection.execute(sql)
        return result
