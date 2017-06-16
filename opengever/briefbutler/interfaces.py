from zope.interface import Interface


class IBriefButler(Interface):

    def send(data):
        """Es macht zueueg"""
