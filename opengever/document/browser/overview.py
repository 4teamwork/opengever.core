from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.base import _ as ogbmf
from opengever.base.browser import edit_public_trial
from opengever.base.browser.helper import get_css_class
from opengever.document import _
from opengever.document.document import IDocumentSchema
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.base import DOSSIER_STATES_CLOSED
from opengever.ogds.base.interfaces import IContactInformation
from opengever.tabbedview.browser.tabs import OpengeverTab
from plone.directives.dexterity import DisplayForm
from Products.CMFCore.utils import getToolByName
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getUtility, queryMultiAdapter

try:
    from opengever.pdfconverter.behaviors.preview import IPreviewMarker
    from opengever.pdfconverter.behaviors.preview import IPreview
    from opengever.pdfconverter.behaviors.preview import \
        CONVERSION_STATE_READY

    PDFCONVERTER_AVAILABLE = True
except ImportError:
    PDFCONVERTER_AVAILABLE = False


class BaseRow(object):
    """Base class for metadata row configurations.
    """
    def __init__(self):
        self._view = None

    def bind(self, view):
        self._view = view

    @property
    def view(self):
        if self._view is None:
            raise Exception("Not bound to a view yet!")
        return self._view


class FieldRow(BaseRow):
    """A metadata row type that gets its information from schema fields.
    """
    def __init__(self, field, label=None):
        super(FieldRow, self).__init__()
        self.field = field
        self.label = label

    def __repr__(self):
        return "<%s for '%s'>" % (self.__class__.__name__, self.field)

    def available(self):
        return self.field in self.view.w

    def get_label(self):
        if self.label is not None:
            return self.label

        widget = self.view.w[self.field]
        if isinstance(widget, SingleCheckBoxWidget):
            label = widget.items[0]['label']
        else:
            label = widget.label
        return label

    def get_content(self):
        widget = self.view.w[self.field]
        if isinstance(widget, SingleCheckBoxWidget):
            content = self._render_boolean_field(widget)
        else:
            content = widget.render()
        return content

    def _render_boolean_field(self, widget):
        value = widget.items[0]['checked']
        yes = _('label_yes', default='yes')
        no = _('label_no', default='no')
        return bool(value) and yes or no


class CustomRow(BaseRow):
    """A custom metadata row type that uses a callable `renderer` to
    fetch the row's content.
    """
    def __init__(self, renderer, label):
        super(CustomRow, self).__init__()
        self.renderer = renderer
        self.label = label

    def available(self):
        return True

    def get_label(self):
        return self.label

    def get_content(self):
        return self.renderer()


class Overview(DisplayForm, OpengeverTab):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-overview')
    grok.template('overview')

    show_searchform = False

    def get_metadata_config(self):
        return [
            FieldRow('title'),
            FieldRow('IDocumentMetadata.document_date'),
            FieldRow('IDocumentMetadata.document_type'),
            FieldRow('IDocumentMetadata.document_author'),
            CustomRow(self.render_creator_link,
                      label=_('label_creator', default='creator')),
            FieldRow('IDocumentMetadata.description'),
            FieldRow('IDocumentMetadata.foreign_reference'),
            CustomRow(self.render_checked_out_link,
                      label=_('label_checked_out', default='Checked out')),
            CustomRow(self.render_file_widget,
                      label=_('label_file', default='File')),
            FieldRow('IDocumentMetadata.digitally_available'),
            FieldRow('IDocumentMetadata.preserved_as_paper'),
            FieldRow('IDocumentMetadata.receipt_date'),
            FieldRow('IDocumentMetadata.delivery_date'),
            FieldRow('IRelatedDocuments.relatedItems'),
            FieldRow('IClassification.classification'),
            FieldRow('IClassification.privacy_layer'),
            CustomRow(self.render_public_trial_with_edit_link,
                      label=ogbmf('label_public_trial',
                                  default='Public Trial')),
            FieldRow('IClassification.public_trial_statement'),
        ]

    def get_metadata_rows(self):
        for row in self.get_metadata_config():
            row.bind(self)
            if not row.available():
                continue
            data = dict(label=row.get_label(),
                        content=row.get_content())
            yield data

    def render_file_widget(self):
        template = ViewPageTemplateFile('overview_templates/file.pt')
        return template(self)

    def render_creator_link(self):
        info = getUtility(IContactInformation)
        return info.render_link(self.context.Creator())

    def render_checked_out_link(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if manager.checked_out():
            info = getUtility(IContactInformation)
            return info.render_link(manager.checked_out())

        return ''

    def get_css_class(self):
        return get_css_class(self.context)

    def is_preview_supported(self):
        # XXX TODO: should be persistent called two times
        if PDFCONVERTER_AVAILABLE:
            return IPreviewMarker.providedBy(self.context)
        return False

    def is_pdf_download_available(self):
        if self.is_preview_supported():
            if IPreview(
                    self.context).conversion_state == CONVERSION_STATE_READY:
                return True
        return False

    def is_checkout_and_edit_available(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if manager.checked_out():
            if manager.checked_out() == \
                    getSecurityManager().getUser().getId():
                return True
            else:
                return False

        return manager.is_checkout_allowed()

    def is_download_copy_available(self):
        """Disable copy link when the document is checked
        out by an other user."""

        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)
        if manager.checked_out():
            if manager.checked_out() != getSecurityManager().getUser().getId():
                return False
        return True

    def render_public_trial_with_edit_link(self):
        template = ViewPageTemplateFile('overview_templates/public_trial.pt')
        return template(self)

    def show_modfiy_public_trial_link(self):
        try:
            can_edit = edit_public_trial.can_access_public_trial_edit_form(
                getSecurityManager().getUser(),
                self.context)
        except (AssertionError, ValueError):
            return False

        wftool = getToolByName(self.context, 'portal_workflow')
        state = wftool.getInfoFor(aq_parent(aq_inner(self.context)),
                                  'review_state')

        return can_edit and state in DOSSIER_STATES_CLOSED
