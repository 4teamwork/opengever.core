from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task
from opengever.globalindex.utils import indexed_task_link_helper
from plone.app.contentlisting.interfaces import IContentListingObject
from Products.ZCatalog.interfaces import ICatalogBrain
from z3c.form.interfaces import IFieldWidget


class BoxesViewMixin(object):

    def render_globalindex_task(self, item):
        return indexed_task_link_helper(item, item.title)

    def get_item_css_classes(self, item):
        """Return all css classes for item.
        """
        return " ".join(["rollover-breadcrumb", get_css_class(item)])

    def get_type(self, item):
        """differ the object typ and return the type as string"""

        if isinstance(item, dict):
            return 'dict'
        elif ICatalogBrain.providedBy(item):
            return 'brain'
        elif IContentListingObject.providedBy(item):
            return 'contentlistingobject'
        elif IFieldWidget.providedBy(item):
            return 'widget'
        elif isinstance(item, Task):
            return 'globalindex_task'
        else:
            raise ValueError("Unknown item type: {!r}".format(item))
