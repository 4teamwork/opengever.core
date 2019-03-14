from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.base import _
from opengever.base.behaviors.utils import set_attachment_content_disposition
from plone import api
from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
import json


class BaseReporterView(BrowserView):
    """Base class for XLS Reporting views, which provide the functionality
    to use the users grid settings (visible columns, column order).
    """

    @property
    def _columns(self):
        """Returns a list of dicts of all available excel columns.
        """
        raise NotImplementedError

    def columns(self):
        return self.filter_and_order_by_tabbedview_settings(self._columns)

    def filter_and_order_by_tabbedview_settings(self, excel_columns):
        excel_columns_by_name = {
            item.get('sort_index', item.get('id')): item for (item) in excel_columns}
        active_columns = []
        tabbedview_columns = self.get_active_tabbedview_columns()
        if not tabbedview_columns:
            return excel_columns

        for col in tabbedview_columns:
            attribute = excel_columns_by_name.get(col.get('id'))
            if attribute:
                active_columns.append(attribute)

        return active_columns

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

    def get_active_tabbedview_columns(self):
        """Loads corresponding tabbedview grid-state and returns an orderd
        list of the current visible columns.
        """
        view_name = self.request.form.get('view_name', None)
        grid_state = self.get_grid_state(view_name)
        if grid_state:
            return [col for col in
                    grid_state.get('columns') if not col.get('hidden')]

    def return_excel(self, reporter):
        data = reporter()
        if not data:
            msg = _(u'Could not generate the report.')
            api.portal.show_message(msg, request=self.request, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE
        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(self.request, self.filename)

        return data
