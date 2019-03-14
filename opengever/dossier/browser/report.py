from ftw.dictstorage.interfaces import IDictStorage
from ftw.tabbedview.interfaces import IGridStateStorageKeyGenerator
from opengever.base.behaviors.utils import set_attachment_content_disposition
from opengever.base.reporter import DATE_NUMBER_FORMAT
from opengever.base.reporter import readable_author
from opengever.base.reporter import StringTranslater, XLSReporter
from opengever.base.reporter import value
from opengever.dossier import _
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryMultiAdapter
import json


class DossierReporter(BrowserView):
    """View that generate an excel spreadsheet with the XLSReporter,
    which list the selected dossier (paths in request)
    and their important attributes.
    """

    def get_dossier_attributes(self):
        attributes = [
            {'id': 'Title',
             'sort_index': 'sortable_title',
             'title': _('label_title', default=u'Title'),
             'transform': value},
            {'id': 'start',
             'title': _(u'label_start', default=u'Opening Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'end',
             'title': _(u'label_end', default=u'Closing Date'),
             'number_format': DATE_NUMBER_FORMAT},
            {'id': 'responsible',
             'title': _(u'label_responsible', default='Responsible'),
             'transform': readable_author},
            {'id': 'review_state',
             'title': _('label_review_state', default='Review state'),
             'transform': StringTranslater(self.request, 'plone').translate},
            {'id': 'reference',
             'title': _(u'label_reference_number',
                        default=u'Reference Number')},
        ]

        return self.filter_and_order_by_tabbedview_settings(attributes)

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

    def get_selected_dossiers(self):

        # get the given dossiers
        catalog = getToolByName(self.context, 'portal_catalog')
        dossiers = []
        for path in self.request.get('paths'):
            dossiers.append(
                catalog(path={'query': path, 'depth': 0})[0]
                )
        return dossiers

    def __call__(self):

        if not self.request.get('paths'):
            msg = _(
                u'error_no_items', default=u'You have not selected any items.')
            IStatusMessage(self.request).addStatusMessage(msg, type='error')
            return_temp = self.request.get(
                'orig_template', self.context.absolute_url())

            return self.request.RESPONSE.redirect(return_temp)

        dossiers = self.get_selected_dossiers()

        # generate the xls data with the XLSReporter
        reporter = XLSReporter(
            self.request, self.get_dossier_attributes(), dossiers)

        data = reporter()
        if not data:
            msg = _(u'Could not generate the report.')
            IStatusMessage(self.request).addStatusMessage(
                msg, type='error')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        response = self.request.RESPONSE

        response.setHeader(
            'Content-Type',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        set_attachment_content_disposition(self.request, "dossier_report.xlsx")

        return data
