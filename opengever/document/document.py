
import logging

from zope import schema
import zope.app.file
from z3c.form.browser import checkbox

from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from plone.dexterity.content import Item
from plone.directives import form

from opengever.sqlfile.field import NamedFile

from opengever.document import _

LOG = logging.getLogger('opengever.document')

class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    foreign_reference = schema.TextLine(
            title = _(u'label_foreign_reference', default='Foreign Reference'),
            description = _('help_foreign_reference', default=''),
            required = False,
    )

    receipt_date = schema.Date(
            title = _(u'label_receipt_date', default='Date of receipt'),
            description = _(u'help_receipt_Date', default=''),
            required = False,
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


class Document(Item):

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
