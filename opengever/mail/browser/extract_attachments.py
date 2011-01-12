from Acquisition import aq_inner, aq_parent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime
from five import grok
from ftw.mail.mail import IMail
from ftw.mail.utils import get_attachments, remove_attachments
from ftw.table.interfaces import ITableGenerator
from opengever.document.behaviors import IRelatedDocuments
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.inbox.inbox import IInbox
from opengever.mail import _
from opengever.ogds.base.interfaces import IContactInformation
from plone.dexterity.utils import createContentInContainer
from z3c.relationfield.relation import RelationValue
from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import os.path


from plone.namedfile import HAVE_BLOBS
if HAVE_BLOBS:
    from plone.namedfile import NamedFile as NamedFile
else:
    from plone.namedfile import NamedFile



def attachment_checkbox_helper(item, position):
    attrs = {'type': 'checkbox',
             'class': 'noborder selectable',
             'name': 'attachments:list',
             'id': 'attachment%s' % str(position),
             'value': str(position)}

    return '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                      for k, v in attrs.items()])


def content_type_helper(item, content_type):
    """Display the content type icon.
    """

    site = getSite()
    mtr = getToolByName(site, 'mimetypes_registry')
    purl = getToolByName(site, 'portal_url')

    attrs = {}

    types = mtr.lookup(content_type)
    if types:
        attrs['src'] = os.path.join(purl(), types[0].icon_path)
        attrs['alt'] = attrs['title'] = types[0].name()

    else:
        attrs['src'] = os.path.join(purl(), 'file_icon.gif')
        attrs['alt'] = attrs['title'] = 'File'

    return '<img %s />' % ' '.join(['%s="%s"' % (k, v)
                                    for k, v in attrs.items()])


def downloadable_filename_helper(context):
    """Render filename as a download link
    """

    def _helper(item, filename):
        return '<a href="%s/get_attachment?position=%s">%s</a>' % (
            context.absolute_url(),
            item.get('position'),
            filename)

    return _helper


def human_readable_filesize_helper(context):
    """Render a filesize human readable (e.g. 100 kB)
    """

    def _helper(item, size):
        return context.getObjSize(size=size)

    return _helper


class ExtractAttachments(grok.View):
    """View for extracting attachments from a `ftw.mail` Mail object into
    `opengever.document` Documents within `opengever.dossier` Dossiers.
    """

    grok.context(IMail)
    grok.name('extract_attachments')
    grok.require('zope2.View')
    grok.template('extract_attachments')

    allowed_delete_actions = ('nothing', 'all', 'selected')

    def render_attachment_table(self):
        """Renders a ftw-table of attachments.
        """

        columns = (
            {'column': 'position',
             'column_title': _(u'column_attachment_checkbox',
                               default=u''),
             'transform': attachment_checkbox_helper},

            {'column': 'content-type',
             'column_title': _(u'column_attachment_type',
                               default=u'Type'),
             'transform': content_type_helper},

            {'column': 'filename',
             'column_title': _(u'column_attachment_filename',
                               default=u'Filename'),
             'transform': downloadable_filename_helper(self.context)},

            {'column': 'size',
             'column_title': _(u'column_attachment_size',
                               default=u'Size'),
             'transform': human_readable_filesize_helper(self.context)},
            )

        items = get_attachments(self.context.msg)

        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(items, columns, sortable=False)

    def __call__(self):
        items = get_attachments(self.context.msg)
        if not len(items):
            msg = _(u'error_no_attachments_to_extract',
                    default=u'This mail has no attachments to extract.')
            IStatusMessage(self.request).addStatusMessage(msg, type='warning')
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        elif self.request.get('form.cancelled'):
            return self.request.RESPONSE.redirect(
                self.context.absolute_url())

        elif self.request.get('form.submitted'):
            attachments = self.request.get('attachments')
            if not attachments:
                msg = _(u'error_no_attachments_selected',
                        default=u'You have not selected any attachments.')
                IStatusMessage(self.request).addStatusMessage(msg,
                                                              type='error')
            else:
                attachments = [int(pos) for pos in attachments]
                delete_action = self.request.get('delete_action', 'nothing')
                if delete_action not in self.allowed_delete_actions:
                    raise ValueError('Expected delete action to be one of ' + \
                                         str(self.allowed_delete_actions))

                self.extract_attachments(attachments, delete_action)

                dossier = self.find_parent_dossier()
                return self.request.RESPONSE.redirect(
                    os.path.join(dossier.absolute_url(), '#documents'))

        return grok.View.__call__(self)

    def extract_attachments(self, positions, delete_action):
        dossier = self.find_parent_dossier()

        info = getUtility(IContactInformation)
        mtool = getToolByName(self.context, 'portal_membership')
        member = mtool.getAuthenticatedMember()
        document_author = info.describe(member.getId())

        attachments_to_extract = filter(
            lambda att: att.get('position') in positions,
            get_attachments(self.context.msg))

        # create documents from the selected attachments
        for att in attachments_to_extract:
            pos = att.get('position')

            kwargs = {'title': att.get('filename'),
                      'file': self.get_attachment_as_namedfile(pos),
                      'document_date': datetime.now(),
                      'document_author': document_author,
                      'keywords': ()}

            doc = createContentInContainer(dossier,
                                           'opengever.document.document',
                                           **kwargs)

            # add a reference to the mail
            intids = getUtility(IIntIds)
            iid = intids.getId(self.context)
            IRelatedDocuments(doc).relatedItems = [RelationValue(iid)]

            msg = _(u'info_extracted_document',
                    default=u'Created document ${title}',
                    mapping={'title': doc.Title()})
            IStatusMessage(self.request).addStatusMessage(msg, type='info')

        # delete the attachments from the email message, if needed
        if delete_action in ('all', 'selected'):
            if delete_action == 'selected':
                pos_to_delete = positions

            else:
                # all
                pos_to_delete = [int(att['position']) for att in
                                 get_attachments(self.context.msg)]

            # set the new message file
            msg = remove_attachments(self.context.msg, pos_to_delete)
            self.context.message = NamedFile(
                data=msg.as_string(),
                contentType=self.context.message.contentType,
                filename=self.context.message.filename)

    def get_attachment_as_namedfile(self, pos):
        """Return a namedfile extracted from the attachment in
        position `pos`.
        """

        # get attachment at position pos
        attachment = None
        for i, part in enumerate(self.context.msg.walk()):
            if i == pos:
                attachment = part
                continue

        if not attachment:
            return None

        return NamedFile(data=attachment.get_payload(decode=1),
                         contentType=attachment.get_content_type(),
                         filename=attachment.get_filename().decode('utf-8'))


    def find_parent_dossier(self):
        """Returns the first parent dossier relative to the current context.
        """

        obj = self.context
        while not IDossierMarker.providedBy(obj) and not IInbox.providedBy(obj):
            obj = aq_parent(aq_inner(obj))

            if IPloneSiteRoot.providedBy(obj):
                return ValueError('Site root reached while searching '
                                  'parent dossier.')

        return obj


