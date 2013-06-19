from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from datetime import date
from five import grok
from ftw.datepicker.widget import DatePickerFieldWidget
from opengever.document import _
from opengever.document.interfaces import IDocumentSettings
from opengever.document.interfaces import NO_DOWNLOAD_DISPLAY_MODE
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.mail.behaviors import IMailInAddress
from opengever.tabbedview.browser.tabs import Tasks
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform.interfaces import OMITTED_KEY
from plone.dexterity.content import Item
from plone.directives import form, dexterity
from plone.namedfile.field import NamedBlobFile
from plone.registry.interfaces import IRegistry
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from z3c.form import validator
from z3c.form.browser import checkbox
from zope import schema
from zope.app.intid.interfaces import IIntIds
from zope.component import getUtility
from zope.interface import invariant, Invalid, Interface
import logging
import os.path


LOG = logging.getLogger('opengever.document')
MAIL_EXTENSIONS = ['.eml', '.msg']

# move and omit the changeNote,
# because it's not possible to make a new version when you editing a file
IVersionable.setTaggedValue(FIELDSETS_KEY, [
        Fieldset('common', fields=[
                'changeNote',
                ])
        ])

# TODO: Not Work in plone 4 and the dexterity b2 release
# possibly it can be solved with plone.directives
IVersionable.setTaggedValue(OMITTED_KEY,
    [(Interface, 'changeNote', 'true'), ])


def related_document(context):
    intids = getUtility(IIntIds)
    return intids.getId(context)


class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'title',
            u'description',
            u'keywords',
            u'foreign_reference',
            u'document_date',
            u'receipt_date',
            u'delivery_date',
            u'document_type',
            u'document_author',
            u'file',
            u'digitally_available',
            u'preserved_as_paper',
            u'archival_file',
            u'thumbnail',
            ],
        )

    dexteritytextindexer.searchable('title')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        description=_(u'help_description', default=u''),
        required=False,
        )

    dexteritytextindexer.searchable('keywords')
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        )
    form.widget(keywords=TextLinesFieldWidget)

    foreign_reference = schema.TextLine(
        title=_(u'label_foreign_reference', default='Foreign Reference'),
        description=_('help_foreign_reference', default=''),
        required=False,
        )

    document_date = schema.Date(
        title=_(u'label_document_date', default='Document Date'),
        description=_(u'help_document_date', default=''),
        required=False,
        )

    #workaround because ftw.datepicker wasn't working
    form.widget(document_date=DatePickerFieldWidget)

    document_type = schema.Choice(
        title=_(u'label_document_type', default='Document Type'),
        description=_(u'help_document_type', default=''),
        source=wrap_vocabulary('opengever.document.document_types',
                    visible_terms_from_registry='opengever.document' +
                            '.interfaces.IDocumentType.document_types'),
        required=False,
        )

    dexteritytextindexer.searchable('document_author')
    document_author = schema.TextLine(
        title=_(u'label_author', default='Author'),
        description=_(u'help_author',
                      default="Surname firstname or a userid"
                      "(would be automatically resolved to fullname)"),
        required=False,
        )

#    dexteritytextindexer.searchable('file')
    form.primary('file')
    file = NamedBlobFile(
        title=_(u'label_file', default='File'),
        description=_(u'help_file', default=''),
        required=False,
        )

    form.mode(digitally_available='hidden')
    digitally_available = schema.Bool(
        title=_(u'label_digitally_available', default='Digital Available'),
        description=_(u'help_digitally_available',
            default='Is the Document Digital Availabe'),
        required=False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title=_(u'label_preserved_as_paper', default='Preserved as paper'),
        description=_(u'help_preserved_as_paper', default=''),
        required=False,
        default=True,
        )

    form.omitted('archival_file')
    archival_file = NamedBlobFile(
        title=_(u'label_archival_file', default='Archival File'),
        description=_(u'help_archival_file', default=''),
        required=False,
        )

    form.omitted('thumbnail')
    thumbnail = NamedBlobFile(
        title=_(u'label_thumbnail', default='Thumbnail'),
        description=_(u'help_thumbnail', default=''),
        required=False,
        )

    form.omitted('preview')
    preview = NamedBlobFile(
        title=_(u'label_preview', default='Preview'),
        description=_(u'help_preview', default=''),
        required=False,
        )

    receipt_date = schema.Date(
        title=_(u'label_receipt_date', default='Date of receipt'),
        description=_(u'help_receipt_date', default=''),
        required=False,
        )
    #workaround because ftw.datepicker wasn't working
    form.widget(receipt_date=DatePickerFieldWidget)

    delivery_date = schema.Date(
        title=_(u'label_delivery_date', default='Date of delivery'),
        description=_(u'help_delivery_date', default=''),
        required=False,
        )
    #workaround because ftw.datepicker wasn't working
    form.widget(delivery_date=DatePickerFieldWidget)

    @invariant
    def title_or_file_required(data):
        if not data.title and not data.file:
            raise Invalid(_(u'error_title_or_file_required',
                            default=u'Either the title or the file is '
                            'required.'))

    @invariant
    def file_or_preserved_as_paper(data):
        """ When no digital file exist, the document must be
        preserved in paper.
        """
        if not data.file and not data.preserved_as_paper:
            raise Invalid(
                _(u'error_file_and_preserved_as_paper',
                default=u"You don't select a file and document is also not \
                preserved in paper_form, please correct it."))


class UploadValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """An mail upload as og.document should't be possible,
        it should be added as Mail object (see opengever.mail)"""

        if value and value.filename:
            basename, extension = os.path.splitext(value.filename)
            if extension.lower() in MAIL_EXTENSIONS:
                if IDossierMarker.providedBy(self.context):
                    mail_address = IMailInAddress(
                        self.context).get_email_address()
                else:
                    parent = aq_parent(aq_inner(self.context))
                    mail_address = IMailInAddress(parent).get_email_address()

                raise Invalid(
                    _(u'error_mail_upload',
                    default=u"It's not possible to add E-mails here, please '\
                    'send it to ${mailaddress} or drag it to the dossier '\
                    ' (Dragn'n'Drop).",
                      mapping={'mailaddress': mail_address}))

            return


validator.WidgetValidatorDiscriminators(
    UploadValidator,
    field=IDocumentSchema['file'],
    )

grok.global_adapter(UploadValidator)


# Default values
@form.default_value(field=IDocumentSchema['document_date'])
def default_document_date(data):
    """Set the actual date as default document_date"""
    return date.today()


@form.default_value(field=IDocumentSchema['preserved_as_paper'])
def default_preserved_as_paper(data):
    """Set the client specific default (configured in the registry)."""

    registry = getUtility(IRegistry)
    proxy = registry.forInterface(IDocumentSettings)

    return proxy.preserved_as_paper_default


class Document(Item):

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def surrender(self, relative_to_portal=1):
        return super(Document, self).getIcon(
            relative_to_portal=relative_to_portal)

    def getIcon(self, relative_to_portal=1):
        """Calculate the icon using the mime type of the file
        """
        utool = getToolByName(self, 'portal_url')

        mimetypeitem = self.get_mimetype()
        if not mimetypeitem:
            return self.surrender(relative_to_portal)

        icon = mimetypeitem[0].icon_path

        if relative_to_portal:
            return icon
        else:
            # Relative to REQUEST['BASEPATH1']
            res = utool(relative=1) + '/' + icon
            while res[:1] == '/':
                res = res[1:]
            return res

    def icon(self):
        """for ZMI
        """
        return self.getIcon()

    def get_mimetype(self):
        """Return the mimetype as object. If there is no matching mimetype,
           it returns False.
        """
        mtr = getToolByName(self, 'mimetypes_registry', None)

        field = self.file
        if not field or not field.getSize():
            # there is no file
            return False

        # get icon by content type
        contenttype = field.contentType
        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG.error(
                'MimeTypeException for %s. Error is: %s' % (
                    self.absolute_url(), str(msg)))
        if not mimetypeitem:
            # not found
            return False
        return mimetypeitem


class View(dexterity.DisplayForm):
    grok.context(IDocumentSchema)
    grok.require("zope2.View")

    def updateWidgets(self):
        super(View, self).updateWidgets()
        field = self.groups[0].fields.get('file')
        if field:
            field.mode = NO_DOWNLOAD_DISPLAY_MODE


class ForwardViewlet(grok.Viewlet):
    """Display the message subject
    """
    grok.name('opengever.document.ForwardViewlet')
    grok.context(IDocumentSchema)
    grok.require('zope2.View')
    grok.viewletmanager(IBelowContentTitle)

    def render(self):
        if self.request.get("externaledit", None):
            return '<script language="JavaScript">jq(function(){window.location.href="' + str(
                self.context.absolute_url()) + '/external_edit"})</script>'
        return ''


class RelatedTasks(Tasks):
    grok.context(IDocumentSchema)
    grok.name('tabbedview_view-tasks')

    search_options = {'related_items': related_document}

    def update_config(self):
        Tasks.update_config(self)

        # do not search on this context, search on site
        self.filter_path = None
