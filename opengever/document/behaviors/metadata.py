from collective import dexteritytextindexer
from datetime import date
from ftw.datepicker.widget import DatePickerFieldWidget
from ftw.keywordwidget.field import ChoicePlus
from ftw.keywordwidget.vocabularies import KeywordSearchableAndAddableSourceBinder
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.mail.mail import IMail
from opengever.base.vocabulary import wrap_vocabulary
from opengever.document import _
from opengever.document.interfaces import IDocumentSettings
from opengever.virusscan.validator import validateUploadForFieldIfNecessary
from plone import api
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile
from plone.supermodel import model
from z3c.form import validator
from z3c.form.browser import checkbox
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import invariant


def document_date_default():
    """Set today's date as the default `document_date`"""
    return date.today()


def preserved_as_paper_default():
    """Set the client specific default for `preserved_as_paper`
    (configured in registry).
    """
    return api.portal.get_registry_record(
        'preserved_as_paper_default', interface=IDocumentSettings)


class IDocumentMetadata(model.Schema):
    """Schema behavior for common GEVER document metadata
    """

    model.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'description',
            u'keywords',
            u'foreign_reference',
            u'document_date',
            u'receipt_date',
            u'delivery_date',
            u'document_type',
            u'document_author',
            u'digitally_available',
            u'preserved_as_paper',
            u'thumbnail',
            u'preview',
            ],
        )

    model.fieldset(
        u'archive_file',
        label=_(u'fieldset_archive_file', u'Archive file'),
        fields=[u'archival_file']
    )

    dexteritytextindexer.searchable('description')
    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False,
        missing_value=u'',
        )

    form.widget('keywords', KeywordFieldWidget, new_terms_as_unicode=True, async=True)
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=ChoicePlus(
            source=KeywordSearchableAndAddableSourceBinder()
        ),
        required=False,
        missing_value=(),
        default=(),
    )

    foreign_reference = schema.TextLine(
        title=_(u'label_foreign_reference', default='Foreign Reference'),
        description=_('help_foreign_reference', default=''),
        required=False,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(document_date=DatePickerFieldWidget)
    document_date = schema.Date(
        title=_(u'label_document_date', default='Document Date'),
        description=_(u'help_document_date', default=''),
        required=False,
        defaultFactory=document_date_default,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(receipt_date=DatePickerFieldWidget)
    receipt_date = schema.Date(
        title=_(u'label_receipt_date', default='Date of receipt'),
        description=_(u'help_receipt_date', default=''),
        required=False,
        )

    # workaround because ftw.datepicker wasn't working
    form.widget(delivery_date=DatePickerFieldWidget)
    delivery_date = schema.Date(
        title=_(u'label_delivery_date', default='Date of delivery'),
        description=_(u'help_delivery_date', default=''),
        required=False,
        )

    document_type = schema.Choice(
        title=_(u'label_document_type', default='Document Type'),
        source=wrap_vocabulary(
            'opengever.document.document_types',
            visible_terms_from_registry='opengever.document.'
                                        'interfaces.IDocumentType.'
                                        'document_types'),
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

    form.mode(digitally_available='hidden')
    digitally_available = schema.Bool(
        title=_(u'label_digitally_available', default='Digital Available'),
        required=False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title=_(u'label_preserved_as_paper', default='Preserved as paper'),
        description=_(u'help_preserved_as_paper', default=''),
        required=False,
        defaultFactory=preserved_as_paper_default,
        )

    form.read_permission(archival_file='opengever.document.ModifyArchivalFile')
    form.write_permission(archival_file='opengever.document.ModifyArchivalFile')
    archival_file = NamedBlobFile(
        title=_(u'label_archival_file', default='Archival File'),
        description=_(u'help_archival_file', default=''),
        required=False,
    )

    form.omitted('archival_file_state')
    archival_file_state = schema.Int(
        title=_(u'label_archival_file_state', default='Archival file state'),
        required=False,
    )

    form.omitted('thumbnail')
    thumbnail = NamedBlobFile(
        title=_(u'label_thumbnail', default='Thumbnail'),
        required=False,
        )

    form.omitted('preview')
    preview = NamedBlobFile(
        title=_(u'label_preview', default='Preview'),
        description=_(u'help_preview', default=''),
        required=False,
        )

    form.omitted('gever_url')
    gever_url = schema.TextLine(
        title=_(u'label_gever_url', default=u'GEVER URL'),
        required=False,
        default=u'',
        missing_value=u''
    )

    @invariant
    def scan_for_virus(data):
        if data.archival_file:
            validateUploadForFieldIfNecessary(
                "archival_file", data.archival_file.filename,
                data.archival_file.open(), getRequest())


alsoProvides(IDocumentMetadata, IFormFieldProvider)
