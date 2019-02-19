"""

"""
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.signals import request_finished, request_started
from django.apps import apps

def finshed(**kwargs):
    """"""
    # graph.close()
    # print("====finshed==")

request_finished.connect(finshed, sender=StaticFilesHandler)
