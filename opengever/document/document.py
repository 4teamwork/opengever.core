from Acquisition import aq_inner, aq_parent
from collective import dexteritytextindexer
from five import grok
from ftw.mail.interfaces import IEmailAddress
from opengever.base.browser.helper import get_css_class
from opengever.document import _
from opengever.document.behaviors.related_docs import IRelatedDocuments
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone.autoform import directives as form_directives
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from Products.CMFCore.utils import getToolByName
from Products.MimetypesRegistry.common import MimeTypeException
from z3c.form import validator
from zope import schema
from zope.component import getMultiAdapter
from zope.interface import Invalid
from zope.interface import invariant
import logging
import os.path


# Note: the changeNote field from the IVersionable behavior is being dropped
# and moved in change_note.py - we do this in a separate module to avoid
# setting the tagged values too early (document.py gets imported in many
# places, to get the IDocumentSchema for example)


LOG = logging.getLogger('opengever.document')
MAIL_EXTENSIONS = ['.eml', '.msg']


class IDocumentSchema(form.Schema):
    """ Document Schema Interface
    """

    form.fieldset(
        u'common',
        label=_(u'fieldset_common', u'Common'),
        fields=[
            u'title',
            u'file',
            ],
        )

    dexteritytextindexer.searchable('title')
    form_directives.order_before(title='IDocumentMetadata.description')
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    form.primary('file')
    form_directives.order_after(file='IDocumentMetadata.document_author')
    file = NamedBlobFile(
        title=_(u'label_file', default='File'),
        description=_(u'help_file', default=''),
        required=False,
        )


    @invariant
    def title_or_file_required(data):
        if not data.title and not data.file:
            raise Invalid(_(u'error_title_or_file_required',
                            default=u'Either the title or the file is '
                            'required.'))


class UploadValidator(validator.SimpleFieldValidator):

    def validate(self, value):
        """An mail upload as og.document should't be possible,
        it should be added as Mail object (see opengever.mail)"""

        if value and value.filename:
            basename, extension = os.path.splitext(value.filename)
            if extension.lower() in MAIL_EXTENSIONS:
                if IDossierMarker.providedBy(self.context):
                    mail_address = IEmailAddress(self.request
                        ).get_email_for_object(self.context)
                else:
                    parent = aq_parent(aq_inner(self.context))
                    mail_address = IEmailAddress(self.request
                        ).get_email_for_object(parent)

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


class Document(Item):

    # disable file preview creation when modifying or creating document
    buildPreview = False

    def surrender(self, relative_to_portal=1):
        return super(Document, self).getIcon(
            relative_to_portal=relative_to_portal)

    def css_class(self):
        return get_css_class(self)

    def related_items(self):
        relations = IRelatedDocuments(self).relatedItems
        if relations:
            return [rel.to_object for rel in relations]
        return []

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

    def checked_out_by(self):
        manager = getMultiAdapter((self, self.REQUEST),
                                  ICheckinCheckoutManager)
        return manager.get_checked_out_by()

    def is_checked_out(self):
        return self.checked_out_by() is not None
