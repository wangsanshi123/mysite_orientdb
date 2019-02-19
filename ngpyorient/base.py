"""

"""
from django.db.models import Q


class In(object):
    """"""
    action = "select"

    def __init__(self, label=None):
        self.label = label

    def __str__(self):
        if type(self.label) == str:
            result = "in(\'{}\')".format(self.label) if self.label else "in()"
        else:
            result = "in('{}')".format(self.label.__name__) if self.label else "in()"
        return result


class Out(In):
    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        if type(self.label) == str:
            result = "out(\'{}\')".format(self.label) if self.label else "out()"
        else:
            result = "out('{}')".format(self.label.__name__) if self.label else "out()"
        return result


class Both(In):
    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        if type(self.label) == str:
            result = "both(\'{}\')".format(self.label) if self.label else "both()"
        else:
            result = "both('{}')".format(self.label.__name__) if self.label else "both()"
        return result


class InT(In):
    """"""
    action = "traverse"

    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        return super().__str__()


class OutT(Out):
    """"""
    action = "traverse"

    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        return super().__str__()


class BothT(Both):
    """"""
    action = "traverse"

    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        return super().__str__()


class InE(In):
    """"""

    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        if type(self.label) == str:
            result = "ine(\'{}\')".format(self.label) if self.label else "ine()"
        else:
            result = "ine('{}')".format(self.label.__name__) if self.label else "ine()"
        return result


class OutE(In):
    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        if type(self.label) == str:
            result = "oute(\'{}\')".format(self.label) if self.label else "oute()"
        else:
            result = "oute('{}')".format(self.label.__name__) if self.label else "oute()"
        return result


class BothE(In):
    def __init__(self, label=None):
        super().__init__(label)

    def __str__(self):
        if type(self.label) == str:
            result = "bothe(\'{}\')".format(self.label) if self.label else "bothe()"
        else:
            result = "bothe('{}')".format(self.label.__name__) if self.label else "bothe()"
        return result


class Q(Q):
    action = "start"

    def __or__(self, other):
        if self.action == other.action:
            return self._combine(other, self.OR)
        else:
            raise Exception("can not operate Q with QE")

    def __and__(self, other):
        if self.action == other.action:
            return self._combine(other, self.AND)
        else:
            raise Exception("can not operate Q with QE")

    pass


class QE(Q):
    """
    Q query for end node
    先找到对应的终点,然后对终点的相关属性做过滤
    """
    action = "end"
