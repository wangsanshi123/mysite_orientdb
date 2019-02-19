"""

"""
from django.core import signals

from ngpyorient.connectionhandler import ConnectionHandler, DEFAULT_DB_ALIAS

from pyorient.ogm import declarative

Node = declarative.declarative_node()
Relationship = declarative.declarative_relationship()

connections = ConnectionHandler()


class DefaultConnectionProxy(object):
    """
    Proxy for accessing the default DatabaseWrapper object's attributes. If you
    need to access the DatabaseWrapper object itself, use
    connections[DEFAULT_DB_ALIAS] instead.
    """

    def __getattr__(self, item):
        return getattr(connections[DEFAULT_DB_ALIAS], item)

    def __setattr__(self, name, value):
        return setattr(connections[DEFAULT_DB_ALIAS], name, value)

    def __delattr__(self, name):
        return delattr(connections[DEFAULT_DB_ALIAS], name)

    def __eq__(self, other):
        return connections[DEFAULT_DB_ALIAS] == other

    def __ne__(self, other):
        return connections[DEFAULT_DB_ALIAS] != other


connection = DefaultConnectionProxy()


# Register an event to reset transaction state and close connections past
# their lifetime.
def close_old_connections(**kwargs):
    for conn in connections.all():
        conn.close()


signals.request_started.connect(close_old_connections)
signals.request_finished.connect(close_old_connections)
