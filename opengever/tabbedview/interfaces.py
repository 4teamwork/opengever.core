from ftw.table.interfaces import ICatalogTableSourceConfig
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import Interface


class ITabbedViewEnabled(Interface):
    """TabbedView behaviour"""


class IGeverTableSourceConfig(ITableSourceConfig):
    pass


class IGeverCatalogTableSourceConfig(IGeverTableSourceConfig, ICatalogTableSourceConfig):
    pass
