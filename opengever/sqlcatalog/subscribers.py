from opengever.sqlcatalog.interfaces import ISQLCatalog
from zope.component import getUtility



def update_catalog(obj, event):
    """This event subscriber makes sure that the object is indexed in the sql catalog.
    """
    catalog = getUtility(ISQLCatalog)
    if catalog.is_supported(obj):
        catalog.index(obj)
