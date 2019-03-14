from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
import json


class BaseReporterView(BrowserView):
    """Base class for XLS Reporting views, which provide the functionality
    to use the users grid settings (visible columns, column order).
    """

    @property
    def _attributes(self):
        """returns a list of dicts of all available attributes (excel columns).
        """
        raise NotImplementedError

    def attributes(self):
        return self.filter_and_order_by_tabbedview_settings(self._attributes)

    def filter_and_order_by_tabbedview_settings(self, attributes):
        attributes_dict = {
            item.get('sort_index', item.get('id')): item for (item) in attributes}
        active_attributes = []
        active_columns = self.get_active_columns()
        if not active_columns:
            return attributes

        for col in active_columns:
            attribute = attributes_dict.get(col.get('id'))
            if attribute:
                active_attributes.append(attribute)

        return active_attributes

    def get_grid_state(self, view_name):
        """Load tabbedview gridstate of the logged in users for the given view.
        """
        tabbedview = self.context.restrictedTraverse(
            "@@tabbedview_view-{}".format(view_name), default=None)
        if not tabbedview:
            return None

        generator = queryMultiAdapter((self.context, tabbedview, self.request),
                                      IGridStateStorageKeyGenerator)
        key = generator.get_key()
        storage = IDictStorage(tabbedview)
        return json.loads(storage.get(key, '{}'))

    def get_active_columns(self):
        """Loads corresponding tabbedview grid-state and returns an orderd
        list of the current visible columns.
        """
        view_name = self.request.form.get('view_name', None)
        grid_state = self.get_grid_state(view_name)
        if grid_state:
            return [col for col in
                    grid_state.get('columns') if not col.get('hidden')]
