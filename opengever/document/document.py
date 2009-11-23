

import logging

from Acquisition import aq_inner
from ZODB.POSException import ConflictError
from five import grok
from z3c.form.browser import checkbox
from zope import schema

from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.dexterity.content import Item
from plone.directives import form
from plone.indexer import indexer
from plone.app.iterate.interfaces import IWorkingCopy

from opengever.sqlfile.field import NamedFile
from plone.namedfile.interfaces import INamedFileField

from opengever.document import _

LOG = logging.getLogger('opengever.document')

from DateTime import DateTime

class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    form.fieldset(
        u'dates',
        label = _(u'fieldset_dates', u'Dates'),
        fields = [
            u'receipt_date',
            u'delivery_date',
            ]
        )

    foreign_reference = schema.TextLine(
        title = _(u'label_foreign_reference', default='Foreign Reference'),
        description = _('help_foreign_reference', default=''),
        required = False,
        )

    document_date = schema.Date(
        title = _(u'label_document_date', default='Document Date'),
        description = _(u'help_document_date', default=''),
        required = True,
        )

    form.primary('file')
    file = NamedFile(
        title = _(u'label_file', default='File'),
        description = _(u'help_file', default=''),
        required = False,
        )

    form.widget(paper_form=checkbox.SingleCheckBoxFieldWidget)
    paper_form = schema.Bool(
        title = _(u'label_paper_form', default='Paper form'),
        description = _(u'help_paper_form', default='Available in paper form only'),
        required = False,
        )

    form.widget(preserved_as_paper=checkbox.SingleCheckBoxFieldWidget)
    preserved_as_paper = schema.Bool(
        title = _(u'label_preserved_as_paper', default='Preserved as paper'),
        description = _(u'help_preserved_as_paper', default=''),
        required = False,
        default = True,
        )

    form.omitted('archival_file')
    archival_file = NamedFile(
        title = _(u'label_archival_file', default='Archival File'),
        description = _(u'help_archival_file', default=''),
        required = False,
        )

    form.omitted('thumbnail')
    thumbnail = NamedFile(
        title = _(u'label_thumbnail', default='Thumbnail'),
        description = _(u'help_thumbnail', default=''),
        required = False,
        )

    form.omitted('preview')
    preview = NamedFile(
        title = _(u'label_preview', default='Preview'),
        description = _(u'help_preview', default=''),
        required = False,
        )

    receipt_date = schema.Date(
        title = _(u'label_receipt_date', default='Date of receipt'),
        description = _(u'help_receipt_date', default=''),
        required = False,
        )

    delivery_date = schema.Date(
        title = _(u'label_delivery_date', default='Date of delivery'),
        description = _(u'help_delivery_date', default=''),
        required = False,
        )


class Document(Item):

    def Title(self):
        title = Item.Title(self)
        if IWorkingCopy.providedBy(self):
            return '%s (WorkingCopy)' % title
        return title

    def getIcon(self, relative_to_portal=0):
        """Calculate the icon using the mime type of the file
        """
        surrender = lambda :super(Document, self).getIcon(relative_to_portal=relative_to_portal)
        mtr   = getToolByName(self, 'mimetypes_registry', None)
        utool = getToolByName(self, 'portal_url')

        field = self.file
        if not field or not field.getSize():
            # there is no file
            return surrender()

        # get icon by content type
        contenttype       = field.contentType
        contenttype_major = contenttype and contenttype.split('/')[0] or ''
        mimetypeitem = None
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException, msg:
            LOG.error('MimeTypeException for %s. Error is: %s' % (self.absolute_url(), str(msg)))
        if not mimetypeitem:
            # not found
            return surrender()
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


@indexer(IDocumentSchema)
def SearchableText( obj ):
    context = aq_inner( obj )
    transforms = getToolByName(obj, 'portal_transforms')
    fields = [
        schema.getFields( IBasic ).get( 'title' ),
        schema.getFields( IBasic ).get( 'description' ),
        schema.getFields( IDocumentSchema ).get('file'),
        ]
    searchable = []
    for field in fields:
        data = field.get( context )
        if not data:
            continue
        if INamedFileField.providedBy( field ):
            # we need to convert the file data to string, so we can
            # index it
            datastream = ''
            try:
                datastream = transforms.convertTo(
                    "text/plain",
                    data.data,
                    mimetype = data.contentType,
                    filename = data.filename,
                    )
            except (ConflictError, KeyboardInterrupt):
                raise
            except Exception, e:
                LOG.error("Error while trying to convert file contents to 'text/plain' "
                          "in SearchableIndex(document.py): %s" % (e,))
            data = str(datastream)
        if isinstance( data, unicode ):
            data = data.encode( 'utf8' )
        if data:
            searchable.append( data )
    return ' '.join( searchable )
grok.global_adapter(SearchableText, name='SearchableText')

class View(grok.View):
    grok.context(IDocumentSchema)
    grok.require("zope2.View")