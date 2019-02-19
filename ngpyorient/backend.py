"""

"""
from django.db.backends.signals import connection_created
from pyorient.ogm import Config

from ngpyorient.graph import NgGraph


class DatabaseWrapper(object):
    """"""
    vendor = 'orientdb'

    def __init__(self, settings_dict, alias="default"):
        self.connection = None
        self.settings_dict = settings_dict
        self.alias = alias

    def get_new_connection(self, conn_params):
        config = Config.from_url(*conn_params)
        conn = NgGraph(config)
        return conn

    def close(self):
        """
        Closes the connection to the database.
        """
        if self.connection is None:
            return
        try:
            if self.connection is not None:
                self.connection.close()
        finally:
            self.connection = None

    def execute(self, sql):
        self.ensure_connection()
        return self.connection.client.command(sql)

    def connect(self):
        """Connects to the database. Assumes that the connection is closed."""
        self.connection = self.get_new_connection(self.get_connection_params())
        """发送连接创建的信号"""
        connection_created.send(sender=self.__class__, connection=self)

    def get_connection_params(self):
        settings_dict = self.settings_dict
        return settings_dict['URL'], settings_dict['USER'], settings_dict['PASSWORD']

    def ensure_connection(self):
        """
        Guarantees that a connection to the database is established.
        """
        if self.connection is None:
            self.connect()

    def update_records_with_transaction(self, queryset):
        return self.connection.update_records_with_transaction(queryset.to_up_ids, queryset.set_args)
