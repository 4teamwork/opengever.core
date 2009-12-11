from zope import schema
from zope.interface import Interface

# -*- extra stuff goes here -*-

class IDossierContainerTypes(Interface):
    """A type for collaborative spaces."""
    
    container_types = schema.List(title=u"container_types", default=['Ordner','Schachtel',])