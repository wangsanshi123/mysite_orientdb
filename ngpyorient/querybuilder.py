"""

"""
import hashlib
import re

from ngpyorient import ng_node
from ngpyorient import ng_relationship
from ngpyorient.match import check_create_args, process_q_args, DEFAULT_FILTER_TERMS, IDS, process_qe_args, \
    process_raw_q_args

_UNARY_OPERATORS = ("IS NULL", "IS NOT NULL")


class QueryBuilder(object):
    def __init__(self, queryset):
        self.queryset = queryset
        self._ast = {"select": []}
        self._query_params = {}
        self._place_holder_registry = {}
        self.annotations = {}
        self.skip = None
        self.limit = None

    def build_where_stmt(self, filters):
        """
        construct a where statement from some filters
        """
        if filters and len(filters):
            stmts = []
            # check whether the prop is the metaproperty
            for row in filters:
                for prop, op_and_val in row.items():
                    if prop in DEFAULT_FILTER_TERMS:
                        row.pop(prop)
                        prop = "@" + prop
                        row[prop] = op_and_val

            for row in filters:

                for prop, op_and_val in row.items():
                    op, val = op_and_val
                    if op in _UNARY_OPERATORS:
                        # unary operators do not have a parameter
                        statement = "{} {}".format(prop, op)
                    else:
                        place_holder = self._register_place_holder(prop)
                        statement = "{} {} {{{}}}".format(prop, op, place_holder)
                        self._query_params[place_holder] = val
                    stmts.append(statement)
            self._ast["where"] = []
            if stmts:
                self._ast["where"].append(" AND ".join(stmts))

        # build Q()
        qs = self.queryset.manager.qs + self.queryset.qs
        if qs and len(qs):
            ls = process_q_args(self.queryset.manager.source_class, qs)
            # build where statement of Q
            if "where" not in self._ast:
                self._ast["where"] = []
            for item in ls:
                connector, expressons = item
                stmts = []
                for item_ in expressons:
                    prop, op, val = item_
                    place_holder = self._register_place_holder(prop)
                    # todo: 因为带逗号字符串在用str.format()中作为key会出错, 所以就替换掉才行
                    place_holder = place_holder.replace(".", "_")
                    statement = "{} {} {{{}}}".format(prop, op, place_holder)
                    self._query_params[place_holder] = val
                    stmts.append(statement)
                if connector == "AND":
                    self._ast["where"].append(" AND ".join(stmts))
                else:
                    self._ast["where"].append("(" + " OR ".join(stmts) + ")")
        pass

    def _register_place_holder(self, key):
        if key in self._place_holder_registry:
            self._place_holder_registry[key] += 1
        else:
            self._place_holder_registry[key] = 1
        return key + "_" + str(self._place_holder_registry[key])

    def build_query(self):
        """
       [{'name': ('=', 'zhang'), 'age': ('<=', 1)}]
        """
        where_sql = ""

        source_class = self.queryset.manager.source_class
        filters = self.queryset.filters + self.queryset.manager.filters
        self.build_where_stmt(filters)
        if "where" in self._ast and self._ast["where"]:
            where_sql += " WHERE "
            where_sql += " AND ".join(self._ast["where"])
        return self.merge_sql(where_sql, source_class)

    def merge_sql(self, where_sql, source_class):
        self.format_params(self._query_params)
        annotations = self.build_annotations()
        if annotations:
            sql = "select {} from {}".format(annotations, source_class.__name__) + where_sql.format(
                **self._query_params)
        else:
            sql = "select from {}".format(source_class.__name__) + where_sql.format(**self._query_params)

        skip_limit = self.build_skip_limit()
        if skip_limit:
            sql = sql + skip_limit
        return sql

    def build_annotations(self):
        result = ",".join([key + " as " + item for key, item in self.annotations.items()])
        return result

    def add_annotation(self, annotation, alias):
        self.annotations[annotation] = alias

    def add_skip_limit(self, skip=None, limit=None):
        self.skip = skip
        self.limit = limit

    def build_skip_limit(self):
        if self.skip and self.limit:
            return "skip {} limit {}".format(self.skip, self.limit)
        elif self.skip and not self.limit:
            return "skip {}".format(self.skip)
        elif not self.skip and self.limit:
            return "limit {}".format(self.limit)

    def format_params(self, params):
        """format paramat--->add quote when necessay"""
        for key, value in params.items():
            if type(value) == str and key.split("_")[0] not in IDS:
                params[key] = "\'" + value + "\'"


class CreateQueryBuilder(QueryBuilder):
    """"""

    def __init__(self, queryset):
        self.queryset = queryset
        self._ast = {"create": []}

    def build_query(self):
        """
        vertex:CREATE VERTEX Employee CONTENT { "name" : "Jay", "surname" : "Miner" }
        edge:CREATE EDGE FROM #10:3 TO #11:4 SET brand = 'fiat'
        :return:
        """
        source_class = self.queryset.manager.source_class
        check_create_args(source_class, self.queryset.manager.kwargs)

        if ng_node.NgNode in source_class.__mro__:
            ""
            sql = "create vertex {} content {}".format(source_class.__name__, self.queryset.manager.kwargs)
            pass
        elif ng_relationship.NgRelationship in source_class.__mro__:
            ""
            out_ = self.queryset.manager.out_
            in_ = self.queryset.manager.in_
            self.check(out_)
            self.check(in_)

            # generate md5 to confirm the out_ and to is unique
            hl = hashlib.md5()
            hl.update((out_ + in_).encode(encoding='utf8'))
            md5 = hl.hexdigest()

            sql = "create edge {} from {} to {} set md5 = {}".format(source_class.__name__, out_, in_,
                                                                     "\'" + md5 + "\'")
        else:
            raise Exception("the class {} is either vertex nor edge".format(source_class))
        return sql

    def check(self, record_id):
        if type(record_id) != str:
            raise Exception("{} is not a record id,record id should be like '#12:03'".format(record_id))
        result = re.match(r"#\d+:\d+", record_id)
        if result == None or result.group() != record_id:
            raise Exception("{} is not a record id,record id should be like '#12:03'".format(record_id))


class UpdateQueryBuilder(QueryBuilder):
    """"""

    def __init__(self, queryset):
        super().__init__(queryset)
        self.queryset = queryset
        self._ast = {"set": []}
        self._set_params = {}

    def build_query(self):
        """
        :return:
        """
        source_class = self.queryset.manager.source_class
        set_args = self.queryset.set_args
        filters = self.queryset.filters + self.queryset.manager.filters
        self.build_where_stmt(filters)
        self.build_set_stmt(set_args, source_class)
        where_sql = ""
        if "where" in self._ast and self._ast["where"]:
            where_sql = " WHERE "
            where_sql += " AND ".join(self._ast["where"])

        return self.merge_sql(where_sql, source_class)

    def build_set_stmt(self, set_args, source_class):
        """
        #update vertex
        update Person set name='yuan1',age=12  WHERE name = 'zhan4'


        #update edge
        UPDATE EDGE Friend SET out = (SELECT FROM Person WHERE name = 'John') WHERE foo = 'bar'
        UPDATE EDGE Likes SET in = #203:0 where in = #202:0
        update edge Likes set in=#171:0,out=#105:0,md5='123',tag='yuan' WHERE in = #172:0 and out =#106:0
        """
        if ng_node.NgNode in source_class.__mro__:
            # self._ast["set"].append("content {}".format(set_args))
            stmts = []
            for prop, val in set_args.items():
                place_holder = self._register_place_holder(prop)
                statement = "{} = {{{}}}".format(prop, place_holder)
                self._set_params[place_holder] = val
                stmts.append(statement)
            if stmts:
                self._ast["set"].append(" , ".join(stmts))
            pass
        elif ng_relationship.NgRelationship in source_class.__mro__:
            """update relation"""
            stmts = []
            for prop, val in set_args.items():
                place_holder = self._register_place_holder(prop)
                statement = "{} = {{{}}}".format(prop, place_holder)
                self._set_params[place_holder] = val
                stmts.append(statement)
            # generate new  md5 when update out or in of edge
            filters = self.queryset.filters + self.queryset.manager.filters

            flag = False  # show whether is updating out or in of edge
            out_new = set_args["out"] if "out" in set_args else None  # out maybe to set
            in_new = set_args["in"] if "in" in set_args else None  # in maybe to set
            out_old = None  # out old
            in_old = None  # in old

            for item in filters:
                if "out" in item:
                    flag = True
                    out_old = item["out"]
                if "in" in item:
                    flag = True
                    in_old = item["in"]
            if flag:
                if out_old and in_old:
                    out_real = out_new or out_old[1]  # out really to set
                    in_real = in_new or in_old[1]  # in really to set
                    hl = hashlib.md5()
                    hl.update((out_real + in_real).encode(encoding='utf8'))
                    md5 = hl.hexdigest()
                    prop = "md5"
                    val = md5
                    place_holder = self._register_place_holder(prop)
                    statement = "{} = {{{}}}".format(prop, place_holder)
                    self._set_params[place_holder] = val
                    stmts.append(statement)
                else:
                    raise Exception("the out and in must both be declared when update edge")

            self._ast["set"] = []
            if stmts:
                self._ast["set"].append(" , ".join(stmts))
            pass
        else:
            raise Exception("the class {} is either vertex nor edge".format(source_class))
        pass

    def merge_sql(self, where_sql, source_class):
        self.format_params(self._query_params)
        self.format_params(self._set_params)

        set_sql = " set "
        set_sql += " , ".join(self._ast["set"])
        set_sql = set_sql.format(**self._set_params)
        where_sql = where_sql.format(**self._query_params)
        if ng_node.NgNode in source_class.__mro__:
            """"""
            sql = "update {} {}".format(source_class.__name__, set_sql) + where_sql
            pass
        elif ng_relationship.NgRelationship in source_class.__mro__:
            """"""
            sql = "update edge {} {}".format(source_class.__name__, set_sql) + where_sql
        else:
            raise Exception("the class {} is either vertex nor edge".format(source_class))
        return sql


class DeleteQueryBuilder(QueryBuilder):
    """

    """

    def __init__(self, queryset):
        super().__init__(queryset)

    def build_query(self):
        """
        DELETE VERTEX person WHERE name = "yuan1"
        :return:
        """
        where_sql = ""
        source_class = self.queryset.manager.source_class
        filters = self.queryset.filters + self.queryset.manager.filters
        self.build_where_stmt(filters)
        if "where" in self._ast and self._ast["where"]:
            where_sql += " WHERE "
            where_sql += " AND ".join(self._ast["where"])
        return self.merge_sql(where_sql, source_class)

    def merge_sql(self, where_sql, source_class):
        self.format_params(self._query_params)

        if ng_node.NgNode in source_class.__mro__:
            sql = "delete vertex {}".format(source_class.__name__) + where_sql.format(**self._query_params)
            ""
        elif ng_relationship.NgRelationship in source_class.__mro__:
            sql = "delete edge {}".format(source_class.__name__) + where_sql.format(**self._query_params)
        else:
            raise Exception("the class {} is either vertex nor edge".format(source_class))

        return sql


class RawQueryBuilder(QueryBuilder):
    def build_query(self):
        # if self.queryset.filter_strs:
        #     sql = "select from ("+self.queryset.raw_query+")"+" where "+self.queryset.filter_strs
        # else:
        #     sql = self.queryset.raw_query
        # return sql
        where_sql = ""

        source_class = self.queryset.manager.source_class
        # filters_related = self.queryset.filters_related
        # self.build_where_stmt(filters_related)
        if "where" in self._ast and self._ast["where"]:
            where_sql += " WHERE "
            where_sql += " AND ".join(self._ast["where"])
        return self.merge_sql(where_sql, source_class)

    def build_where_stmt(self, filters):
        """
        construct a where statement from some filters
        """
        if filters and len(filters):
            stmts = []
            for row in filters:
                for prop, op_and_val in row.items():
                    op, val = op_and_val
                    if op in _UNARY_OPERATORS:
                        # unary operators do not have a parameter
                        statement = "{} {}".format(prop, op)
                    else:
                        place_holder = self._register_place_holder(prop)
                        statement = "{} {} {{{}}}".format(prop, op, place_holder)
                        self._query_params[place_holder] = val
                    stmts.append(statement)
            self._ast["where"] = []
            if stmts:
                self._ast["where"].append(" AND ".join(stmts))

        # build Q()
        qs = self.queryset.manager.qs + self.queryset.qs
        if qs and len(qs):
            ls = process_raw_q_args(self.queryset.manager.source_class, qs)
            # build where statement of Q
            if "where" not in self._ast:
                self._ast["where"] = []
            for item in ls:
                connector, expressons = item
                stmts = []
                for item_ in expressons:
                    prop, op, val = item_
                    place_holder = self._register_place_holder(prop)
                    statement = "{} {} {{{}}}".format(prop, op, place_holder)
                    self._query_params[place_holder] = val
                    stmts.append(statement)
                if connector == "AND":
                    self._ast["where"].append(" AND ".join(stmts))
                else:
                    self._ast["where"].append("(" + " OR ".join(stmts) + ")")
        pass

    def merge_sql(self, where_sql, source_class):
        self.format_params(self._query_params)
        # sql = "select from ({})".format(self.queryset.raw_query) + where_sql.format(**self._query_params)
        # return sql
        annotations = self.build_annotations()
        if annotations:
            sql = "select {} from ({})".format(annotations, self.queryset.raw_query) + where_sql.format(
                **self._query_params)
        else:
            sql = "select from ({})".format(self.queryset.raw_query) + where_sql.format(
                **self._query_params)

        skip_limit = self.build_skip_limit()
        if skip_limit:
            sql = sql + skip_limit
        return sql


class SpanWithSelectQueryBuilder(QueryBuilder):
    """跨表查询---select（明确指明中间关系）"""

    def __init__(self, queryset):
        super().__init__(queryset)
        self._dest_query_params = {}
        self.skip = None
        self.limit = None

    def build_query(self):
        """
       select from (SELECT EXPAND(out('likes').in('have')) FROM person where name="yuan1")  where name ='USA'
       select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where (@class='car' and name='dazhong') or(@class='phone')


        """
        where_sql = ""
        dest_where_sql = ""
        # build relation statement
        source_class = self.queryset.manager.source_class
        relation = self.queryset.manager.relation + self.queryset.relation
        filters = self.queryset.filters + self.queryset.manager.filters
        filters_destination = self.queryset.filters_destination + self.queryset.manager.filters_destination
        self.build_where_stmt(filters)
        self.build_destination_where_stmt(filters_destination)
        self.build_relation_stmt(relation)
        if "where" in self._ast and self._ast["where"]:
            where_sql += " WHERE "
            where_sql += " AND ".join(self._ast["where"])
        if "dest_where" in self._ast and self._ast["dest_where"]:
            dest_where_sql += " WHERE "
            dest_where_sql += " AND ".join(self._ast["dest_where"])

        return self.merge_sql(where_sql, dest_where_sql, source_class)

        pass

    def build_destination_where_stmt(self, filters_destination):
        stmts = []
        # check whether the prop is the metaproperty
        for row in filters_destination:
            for prop, op_and_val in row.items():
                if prop in DEFAULT_FILTER_TERMS:
                    row.pop(prop)
                    prop = "@" + prop
                    row[prop] = op_and_val
        for row in filters_destination:
            for prop, op_val_class in row.items():
                op, val, class_name = op_val_class

                place_holder = self._register_place_holder(prop)
                statement = "{} {} {{{}}}".format(prop, op, place_holder)
                self._dest_query_params[place_holder] = val
                stmts.append(statement)

                prop, op, val = "@class", "=", class_name
                place_holder = self._register_place_holder(prop)
                statement = "{} {} {{{}}}".format(prop, op, place_holder)
                self._dest_query_params[place_holder] = val
                stmts.append(statement)
        self._ast["dest_where"] = []
        if stmts:
            self._ast["dest_where"].append(" AND ".join(stmts))

        # build QE
        qes = self.queryset.manager.qes + self.queryset.qes
        if qes and len(qes):
            ls = process_qe_args(self.queryset.manager.source_class, qes)
            if "dest_where" not in self._ast:
                self._ast["dest_where"] = []
            for item in ls:
                connector, expressons = item
                stmts = []
                for item_ in expressons:
                    prop, op, val, class_name = item_
                    place_holder = self._register_place_holder(prop)
                    statement = "{} {} {{{}}}".format(prop, op, place_holder)
                    self._dest_query_params[place_holder] = val

                    prop, op, val = "@class", "=", class_name
                    place_holder = self._register_place_holder(prop)
                    statement = "(" + statement + " and " + "{} {} {{{}}}".format(prop, op, place_holder) + ")"
                    self._dest_query_params[place_holder] = val

                    stmts.append(statement)
                if connector == "AND":
                    self._ast["dest_where"].append(" AND ".join(stmts))
                else:
                    self._ast["dest_where"].append("(" + " OR ".join(stmts) + ")")

        pass

    def build_relation_stmt(self, relation):
        self.relation_sql = "select EXPAND(" + ".".join([item.__str__() for item in relation]) + ")"

    def merge_sql(self, where_sql, dest_where_sql, source_class):
        """
        select from (SELECT EXPAND(out('likes')) FROM person where name="yuan1") where (@class='car' and name='dazhong') or(@class='phone')
        """
        self.format_params(self._query_params)
        self.format_params(self._dest_query_params)

        # sql = "select from ({} from {} {}) {} ".format(self.relation_sql, source_class.__name__,
        #                                                where_sql.format(**self._query_params),
        #                                                dest_where_sql.format(**self._dest_query_params))
        # return sql
        annotations = self.build_annotations()
        if annotations:
            sql = "select {} from ({} from {} {}) {} ".format(annotations, self.relation_sql, source_class.__name__,
                                                              where_sql.format(**self._query_params),
                                                              dest_where_sql.format(**self._dest_query_params))
        else:
            sql ="select from ({} from {} {}) {} ".format(self.relation_sql, source_class.__name__,
                                                     where_sql.format(**self._query_params),
                                                     dest_where_sql.format(**self._dest_query_params))

        skip_limit = self.build_skip_limit()
        if skip_limit:
            sql = sql + skip_limit

        return sql

    pass


class SpanWithTraverseQueryBuilder(QueryBuilder):
    """跨表查询---traverse（只指定有限关系，查询与指定节点有关系的所有节点，如果不指定深度）"""

    def __init__(self, queryset):
        super().__init__(queryset)
