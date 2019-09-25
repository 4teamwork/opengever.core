from ftw.table.interfaces import ITableGenerator
from opengever.base.utils import disable_edit_bar
from opengever.base.utils import escape_html
from opengever.mail import _
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.Five.browser import BrowserView
from zope.component import getUtility
import os.path


def attachment_checkbox_helper(item, value):
    attrs = {'type': 'checkbox',
             'class': 'noborder selectable',
             'name': 'attachments:list',
             'id': 'attachment%s' % str(item['position']),
             'value': str(item['position'])}

    return '<input %s />' % ' '.join(['%s="%s"' % (k, v)
                                      for k, v in attrs.items()])


def content_type_helper(item, content_type):
    """Display the content type icon.
    """
    mtr = api.portal.get_tool(name='mimetypes_registry')
    normalize = getUtility(IIDNormalizer).normalize

    css_class = 'icon-dokument_verweis'
    if content_type == 'application/octet-stream':
        mimetype = mtr.globFilename(item.get('filename'))
    else:
        result = mtr.lookup(content_type)
        if result and isinstance(result, tuple):
            mimetype = result[0]
        else:
            mimetype = None

    if mimetype:
        # Strip '.gif' from end of icon name and remove leading 'icon_'
        icon_filename = mimetype.icon_path
        filetype = os.path.splitext(icon_filename)[0].replace('icon_', '')
        css_class = 'icon-{}'.format(normalize(filetype))

    return '<span class={} />'.format(css_class)


def downloadable_filename_helper(context):
    """Render filename as a download link
    """

    def _helper(item, filename):
        link = '<a href="%s/get_attachment?position=%s">%s</a>' % (
            context.absolute_url(),
            item.get('position'),
            escape_html(filename))
        return link

    return _helper


def human_readable_filesize_helper(context):
    """Render a filesize human readable (e.g. 100 kB)
    """

    def _helper(item, size):
        return context.getObjSize(size=size)

    return _helper


class ExtractAttachments(BrowserView):
    """View for extracting attachments from a `ftw.mail` Mail object into
    `opengever.document` Documents in a `IMailInAddressMarker` container.
    """

    allowed_delete_actions = ('nothing', 'all', 'selected')

    def render_attachment_table(self):
        """Renders a ftw-table of attachments.
        """

        columns = (
            {'column': '',
             'transform': attachment_checkbox_helper,
             'width': 30},

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

        items = self.context.get_attachments()

        generator = getUtility(ITableGenerator, 'ftw.tablegenerator')
        return generator.generate(items, columns, sortable=False)

    def __call__(self):
        disable_edit_bar()

        if not self.context.has_attachments():
            msg = _(u'error_no_attachments_to_extract',
                    default=u'This mail has no attachments to extract.')
            api.portal.show_message(msg, request=self.request, type='warning')
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        if self.request.get('form.cancelled'):
            return self.request.RESPONSE.redirect(self.context.absolute_url())

        if self.request.get('form.submitted'):
            attachments = self.request.get('attachments')
            if not attachments:
                msg = _(u'error_no_attachments_selected',
                        default=u'You have not selected any attachments.')
                api.portal.show_message(
                    msg, request=self.request, type='error')
            else:
                attachments = [int(pos) for pos in attachments]
                delete_action = self.request.get('delete_action', 'nothing')
                if delete_action not in self.allowed_delete_actions:
                    raise ValueError('Expected delete action to be one of '
                                     + str(self.allowed_delete_actions))

                self.extract_attachments(attachments, delete_action)
                return self.request.RESPONSE.redirect(
                    "{}/#documents".format(
                        self.context.get_extraction_parent().absolute_url()))

        return super(ExtractAttachments, self).__call__()

    def is_delete_attachment_supported(self):
        return self.context.is_delete_attachment_supported()

    def extract_attachments(self, positions, delete_action):
        docs = self.context.extract_attachments_into_parent(positions)
        for document in docs:
            msg = _(u'info_extracted_document',
                    default=u'Created document ${title}',
                    mapping={'title': document.Title().decode('utf-8')})
            api.portal.show_message(msg, request=self.request, type='info')

        if not self.is_delete_attachment_supported():
            return

        # delete the attachments from the email message, if needed
        if delete_action == 'selected':
            self.context.delete_attachments(positions)
        elif delete_action == 'all':
            self.context.delete_all_attachments()

    def get_number_of_attachments(self):
        return len(self.context.get_attachments())
