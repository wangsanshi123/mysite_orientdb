"""
implement some more feature than pyorient
@author:yuantaixing
"""
import logging

from pyorient.ogm import Graph
from pyorient.ogm.query import Query

from ngpyorient import ng_node, ng_relationship


class NgGraph(Graph):
    """extends Graph,but has more feature than graph --next generation graph"""

    def out(self, from_, *edge_classes, **kwargs):
        """Get adjacent outgoing vertexes from vertex or class.

        :param from_: Vertex id, class, or class name
        :param edge_classes: Filter by these edges
        :param **kwargs: conditons
        """

        condition_str = self._get_condition_str(**kwargs)
        if condition_str:
            sql_string = 'SELECT EXPAND( out({0}) ) FROM {1} {2}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(from_), condition_str)
        else:
            sql_string = 'SELECT EXPAND( out({0}) ) FROM {1}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(from_))
        records = self.client.query(sql_string, -1)

        return [self.vertex_from_record(v) for v in records] \
            if records else []

    def in_(self, to, *edge_classes, **kwargs):
        """Get adjacent incoming vertexes to vertex or class.

        :param to: Vertex id, class, or class name
        :param edge_classes: Filter by these edges
        :param **kwargs: conditons
        """

        condition_str = self._get_condition_str(**kwargs)
        if condition_str:
            sql_string = 'SELECT EXPAND( in({0}) ) FROM {1}{2}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(to), condition_str)
        else:
            sql_string = 'SELECT EXPAND( in({0}) ) FROM {1}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(to))
        records = self.client.query(sql_string, -1)
        return [self.vertex_from_record(v) for v in records] \
            if records else []

    def bothE(self, from_to, *edge_classes, **kwargs):
        """Get outgoing/incoming edges from/to vertex or class.

        :param from_to: Vertex id, class, or class name
        :param edge_classes: Filter by these edges
        :param **kwargs: conditons
        """
        condition_str = self._get_condition_str(**kwargs)
        if condition_str:
            sql_string = 'SELECT EXPAND( bothE({0}) ) FROM {1}{2}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(from_to), condition_str)
        else:
            sql_string = 'SELECT EXPAND( bothE({0}) ) FROM {1}'.format(
                ','.join(Graph.coerce_class_names_to_quoted(edge_classes))
                , self.coerce_class_names(from_to))
        records = self.client.query(sql_string, -1)
        return [self.edge_from_record(r) for r in records] \
            if records else []

    def _get_condition_str(self, **kwargs):

        def add_quote(item):
            """add quote to string"""
            if type(item) == str:
                return "\'" + item + "\'"
            else:
                return item

        condition_string = None
        # add condition
        if kwargs:
            header = " where "
            condition_string = header + "".join(["{}={} and " for i in kwargs.items()]).rstrip("and ")
            list_new = [[key, add_quote(value)] for key, value in kwargs.items()]
            key_values = [item for temp in list_new for item in temp]

            condition_string = condition_string.format(*key_values)
        return condition_string

    def delete_records(self, records):
        """delete records"""
        if not records or not len(records):
            raise Exception("records should not be null")
        elif type(records) == Query:
            for record in records:
                cluster_id, position_id = [int(id.lstrip("#")) for id in record._id.split(":")]
                self.client.record_delete(cluster_id, position_id)
        else:
            for record in records:
                cluster_id, position_id = [int(id.lstrip("#")) for id in record._rid.split(":")]
                self.client.record_delete(cluster_id, position_id)

    def update_records(self, records, data):
        """update records -->actually batch update but without transaction"""
        if not records or not len(records):
            raise Exception("records should not be null")
        elif type(records) != list:
            raise Exception(
                """only support query from raw sql by client. eg:graph.client.query("select from person where name='yuantaixing'")""")
        else:
            for record in records:
                cluster_id, position_id = [int(id.lstrip("#")) for id in record._rid.split(":")]
                self.client.record_update(cluster_id, position_id, data, record._version)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def update_records_with_transaction(self, records, data, partial=True):
        """
        update with transaction
        fixme:have bug here:will override the relationship(edge) of vertex
        """
        tx = self.client.tx_commit()

        # Begin Transaction
        tx.begin()

        try:
            # Create Records
            for record in records:
                record.oRecordData.update(data)
                cluster_id, position_id = [int(id.lstrip("#")) for id in record._rid.split(":")]
                new = self.client.record_update(cluster_id, position_id, record.oRecordData, record._version)
                tx.attach(new)
            tx.commit()
        except Exception as e:
            logging.error("update failed because {}".format(e))
            tx.rollback()

    def drop_class_simple(self, cls):
        """"""
        if ng_node.NgNode in cls.__mro__:
            sql = "delete vertex {}".format(cls.__name__)
            ""
        elif ng_relationship.NgRelationship in cls.__mro__:
            sql = "delete edge {}".format(cls.__name__)
        else:
            raise Exception("the class {} is either vertex nor edge".format(cls))
        self.client.command(sql)
        self.client.command("drop class {}".format(cls.__name__))

    def drop_class_simple_by_class_name(self, cls_name, type="vertex"):
        """"""
        if type == "vertex":
            sql = "delete vertex {}".format(cls_name)
            ""
        elif type == "edge":
            sql = "delete edge {}".format(cls_name)
        else:
            raise Exception("the class {} is either vertex nor edge".format(cls_name))
        self.client.command(sql)
        self.client.command("drop class {}".format(cls_name))
