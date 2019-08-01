from AccessControl import getSecurityManager
from ftw import bumblebee
from ftw.bumblebee.interfaces import IBumblebeeDocument
from opengever.base import _ as ogbmf
from opengever.base.behaviors.changed import IChanged
from opengever.base.browser import edit_public_trial
from opengever.base.browser.helper import get_css_class
from opengever.base.utils import to_html_xweb_intelligent
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.document import _
from opengever.document.archival_file import ARCHIVAL_FILE_STATE_MAPPING
from opengever.document.behaviors.metadata import IDocumentMetadata
from opengever.document.browser import archival_file_form
from opengever.document.browser.actionbuttons import VisibleActionButtonRendererMixin
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.base import DOSSIER_STATES_CLOSED
from opengever.meeting import is_meeting_feature_enabled
from opengever.meeting.model import SubmittedDocument
from opengever.ogds.base.actor import Actor
from opengever.tabbedview import GeverTabMixin
from plone import api
from plone.dexterity.browser.view import DefaultView
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.MimetypesRegistry.common import MimeTypeException
from urllib import quote_plus
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.component import queryMultiAdapter


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
        return yes if bool(value) else no


class WebIntelligentFieldRow(FieldRow):
    """Transform the widget value to x-web-intelligent.

    This should only be used for well known fields.
    """

    def get_content(self):
        widget = self.view.w[self.field]
        content = to_html_xweb_intelligent(widget.value)
        return '<div id="{}" class="{}">{}</div>'.format(widget.id, widget.klass, content)


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


class TemplateRow(CustomRow):
    """Row that renders a template.

    The parameter template_name should be the filename (without extension) of
    a template from the templates folder.
    """

    def __init__(self, template, label):
        self.template = template
        super(TemplateRow, self).__init__(self.template, label)

    def get_content(self):
        return self.renderer(self.view)


class Overview(DefaultView, GeverTabMixin, VisibleActionButtonRendererMixin):
    """File details overview.
    """

    is_on_detail_view = True
    is_overview_tab = True

    show_searchform = False

    file_template = ViewPageTemplateFile('templates/file.pt')
    keywords_template = ViewPageTemplateFile('templates/keywords.pt')
    related_documents_template = ViewPageTemplateFile(
        'templates/related_documents.pt')
    archival_file_template = ViewPageTemplateFile('templates/archiv_file.pt')
    public_trial_template = ViewPageTemplateFile('templates/public_trial.pt')
    submitted_with_template = ViewPageTemplateFile('templates/submitted_with.pt')  # noqa

    def get_metadata_config(self):
        rows = [
            FieldRow('title'),
            FieldRow('IDocumentMetadata.document_date'),
            TemplateRow(self.file_template,
                        label=_('label_file', default='File')),
            CustomRow(self.get_creation_date,
                      label=_('label_created', default='Created')),
            CustomRow(self.get_modification_date,
                      label=_('label_modified', default='Modified')),
            FieldRow('IDocumentMetadata.document_type'),
            FieldRow('IDocumentMetadata.document_author'),
            CustomRow(self.render_creator_link,
                      label=_('label_creator', default='creator')),
            WebIntelligentFieldRow('IDocumentMetadata.description'),
            TemplateRow(self.keywords_template,
                        label=_(u'label_keywords', default=u'Keywords')),
            FieldRow('IDocumentMetadata.foreign_reference'),
            CustomRow(self.render_checked_out_link,
                      label=_('label_checked_out', default='Checked out')),
            FieldRow('IDocumentMetadata.digitally_available'),
            FieldRow('IDocumentMetadata.preserved_as_paper'),
            FieldRow('IDocumentMetadata.receipt_date'),
            FieldRow('IDocumentMetadata.delivery_date'),
            TemplateRow(self.related_documents_template, label=_(
                u'label_related_documents', default=u'Related Documents')),
            FieldRow('IClassification.classification'),
            FieldRow('IClassification.privacy_layer'),
            TemplateRow(self.public_trial_template,
                        label=ogbmf('label_public_trial',
                                    default='Public Trial')),
            FieldRow('IClassification.public_trial_statement')
        ]

        if self.is_archivale_file_visible():
            row = TemplateRow(
                self.archival_file_template,
                label=_(u'label_archival_file', default='Archival File'))
            rows.append(row)
            row = CustomRow(self.render_archival_file_state,
                            label=_('label_archival_file_state',
                                    default='Archival file state'))
            rows.append(row)

        if is_meeting_feature_enabled():
            rows.append(TemplateRow(self.submitted_with_template,
                                    label=_('Submitted with')))
        return rows

    def render_archival_file_state(self):
        state = IDocumentMetadata(self.context).archival_file_state
        return ARCHIVAL_FILE_STATE_MAPPING.get(state)

    def get_metadata_rows(self):
        for row in self.get_metadata_config():
            row.bind(self)
            if not row.available():
                continue
            data = dict(label=row.get_label(),
                        content=row.get_content())
            yield data

    def get_meeting_links(self):

        proposal = self.context.get_proposal()
        if proposal is None:
            return

        proposal_model = proposal.load_model()

        proposal_link = proposal_model.get_link()
        if proposal_link:
            yield {
                'label': _('label_proposal', default='Proposal'),
                'content': proposal_link,
            }
        else:
            return

        meeting_link = proposal_model.get_meeting_link()
        if meeting_link:
            yield {
                'label': _('label_meeting', default='Meeting'),
                'content': meeting_link,
            }

    def submitted_documents(self):
        return SubmittedDocument.query.by_source(self.context).all()

    def get_update_document_url(self, submitted_document):
        return ('{}/@@submit_additional_document'
                '?submitted_document_id={}').format(
                    self.context.absolute_url(),
                    submitted_document.document_id
                    )

    def linked_documents(self):
        """Returns a list documents related to the context document.
        """
        return [{
            'class': self.get_css_class(obj),
            'title': obj.Title(),
            'url': obj.absolute_url(),
        } for obj in sorted(
            self.context.related_items(
                bidirectional=True,
                documents_only=True,
                ),
            key=lambda obj: obj.Title()
        )]

    def is_outdated(self, submitted_document):
        return not submitted_document.is_up_to_date(self.context)

    def is_archivale_file_visible(self):
        return api.user.has_permission(
            'opengever.document: Modify archival file',
            obj=self.context)

    def render_submitted_version(self, submitted_document):
        return _(u"Submitted version: ${version}",
                 mapping={'version': submitted_document.submitted_version})

    def render_current_document_version(self):
        version = self.context.get_current_version_id(missing_as_zero=True)
        return _(u"Current version: ${version}", mapping={'version': version})

    def render_creator_link(self):
        return Actor.user(self.context.Creator()).get_link()

    def render_checked_out_link(self):
        manager = queryMultiAdapter(
            (self.context, self.request), ICheckinCheckoutManager)

        if manager.get_checked_out_by():
            return Actor.user(manager.get_checked_out_by()).get_link()
        return ''

    def get_keywords(self):
        linked_keywords = [{
            'url': u'{}/@@search?Subject={}'.format(
                api.portal.get().absolute_url(),
                quote_plus(safe_unicode(keyword).encode('utf-8'))),
            'title': keyword,
        } for keyword in IDocumentMetadata(self.context).keywords]
        return linked_keywords

    def get_css_class(self, context=None):
        return get_css_class(context or self.context)

    def show_modfiy_public_trial_link(self):
        parent_dossier = self.context.get_parent_dossier()
        if not parent_dossier:
            return False

        try:
            can_edit = edit_public_trial.can_access_public_trial_edit_form(
                getSecurityManager().getUser(),
                self.context)
        except (AssertionError, ValueError):
            return False

        state = api.content.get_state(parent_dossier, default=None)
        return can_edit and state in DOSSIER_STATES_CLOSED

    def show_preview(self):
        return is_bumblebee_feature_enabled()

    def preview_image_url(self):
        return bumblebee.get_service_v3().get_representation_url(
            self.context, 'image')

    def get_bumblebee_checksum(self):
        return IBumblebeeDocument(self.context).get_checksum()

    def get_overlay_url(self):
        return '{}/@@bumblebee-overlay-document'.format(
            self.context.absolute_url())

    def show_edit_archival_file_link(self):
        try:
            can_edit = archival_file_form.can_access_archival_file_form(
                api.user.get_current(), self.context)
        except (AssertionError, ValueError):
            return False

        state = api.content.get_state(
            self.context.get_parent_dossier(), default=None)
        return can_edit and state in DOSSIER_STATES_CLOSED

    def get_archival_file_class(self):
        mtr = getToolByName(self, 'mimetypes_registry', None)
        archival_file = IDocumentMetadata(self.context).archival_file
        normalize = getUtility(IIDNormalizer).normalize

        try:
            icon = mtr.lookup(archival_file.contentType)[0].icon_path
            filetype = icon[:icon.rfind('.')].replace('icon_', '')
            return 'icon-%s' % normalize(filetype)

        except MimeTypeException:
            pass

        return 'contenttype-opengever-document-document'

    def get_creation_date(self):
        return self.context.toLocalizedTime(
            self.context.created(), long_format=True)

    def get_modification_date(self):
        return self.context.toLocalizedTime(
            IChanged(self.context).changed, long_format=True)
