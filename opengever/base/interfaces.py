from zope import schema
from zope.interface import Interface

# -*- extra stuff goes here -*-

class IBaseCustodyPeriods(Interface):    
    custody_periods = schema.List(title=u"custody period", default=[u'0', u'10', u'30', u'100', u'150',])

class IBaseClientID(Interface):
    client_id = schema.TextLine(title=u"client id", default=u"OG")