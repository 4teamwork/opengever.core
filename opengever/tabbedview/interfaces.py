from ftw.table.interfaces import ICatalogTableSourceConfig
from ftw.table.interfaces import ITableSourceConfig
from zope.interface import Attribute
from zope.interface import Interface


class ITabbedViewEnabled(Interface):
    """TabbedView behaviour"""


class IGeverTableSourceConfig(ITableSourceConfig):
    pass


class IGeverCatalogTableSourceConfig(IGeverTableSourceConfig, ICatalogTableSourceConfig):
    pass


class IOneoffixxTableSourceConfig(ITableSourceConfig):
    pass


class ITabbedViewProxy(Interface):
    """A tabbedview-view providing this interfaces is a master-tab
    which defines which sub-view should be rendered (bumblebee).
    """

    def render_preferred_view():
        """Renders the current preferred view name
        """

    preferred_view_name = Attribute(
        "Returns the current preferred view name")

    list_view_name = Attribute(
        "Returns the viewname of the listing-view")

    gallery_view_name = Attribute(
        "Returns the viewname of the gallery-view")

    name_without_postfix = Attribute(
        "Returns the viewname without the prefix. "
        "In some cases we need the original tabbedview-name without the"
        "proxy prefix (i.e. to store and load the gridstate")
