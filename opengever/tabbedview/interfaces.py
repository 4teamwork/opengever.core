from ftw.table.interfaces import ICatalogTableSourceConfig
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import Interface


class ITabbedViewEnabled(Interface):
    """TabbedView behaviour"""


class IGeverTableSourceConfig(ITableSourceConfig):
    pass


class IGeverCatalogTableSourceConfig(IGeverTableSourceConfig, ICatalogTableSourceConfig):
    pass


class ITabbedViewProxy(Interface):
    """A tabbedview-view providing this interfaces is a master-tab
    which defines which sub-view should be rendered (bumblebee).
    """
