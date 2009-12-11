from zope import schema
from zope.interface import Interface

# -*- extra stuff goes here -*-

class IBaseCustodyPeriods(Interface):    
    custody_periods = schema.List(title=u"custody period", default=['0', '30', '100', '150',])
