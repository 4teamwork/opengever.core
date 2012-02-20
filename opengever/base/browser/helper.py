from Acquisition import aq_inner, aq_parent
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_client_id
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.deprecation import deprecated


def client_title_helper(item, value):
    """Returns the client title out of the client id (`value`).
    """
    if not value:
        return value

    info = getUtility(IContactInformation)
    client = info.get_client_by_id(value)

    if client:
        return client.title

    else:
        return value


def get_css_class(item):
    """Returns the content-type icon css class for `item`.

    Arguments:
    `item` -- obj or brain
    """

    css_class = None

    normalize = getUtility(IIDNormalizer).normalize
    if item.portal_type == 'opengever.document.document':
        if getattr(item, '_v__is_relation', False):
            # Document was listed as a relation, so we use a special icon.
            css_class = "icon-dokument_verweis"
            # Immediatly set the volatile attribute to False so it doesn't
            # affect other views using the same object instance
            item._v__is_relation = False

        else:
            # It's a document, we therefore want to display an icon
            # for the mime type of the contained file
            icon = getattr(item, 'getIcon', '')
            if callable(icon):
                icon = icon()

            if not icon == '':
                # Strip '.gif' from end of icon name and remove
                # leading 'icon_'
                filetype = icon[:icon.rfind('.')].replace('icon_', '')
                css_class = 'icon-%s' % normalize(filetype)
            else:
                # Fallback for unknown file type
                css_class = "contenttype-%s" % normalize(item.portal_type)

    elif item.portal_type == 'opengever.task.task':
        if hasattr(item, 'is_subtask'):
            # item is a brain
            is_subtask = item.is_subtask
            is_remote_task = item.client_id != item.assigned_client

        else:
            # item is a object
            is_subtask = aq_parent(aq_inner(item)).portal_type \
                == 'opengever.task.task'
            is_remote_task = item.responsible_client != get_client_id()

        if is_subtask:
            css_class = 'icon-task-subtask'

        elif is_remote_task:
            css_class = 'icon-task-remote-task'

    if css_class is None:
        css_class = "contenttype-%s" % normalize(item.portal_type)

    return css_class


css_class_from_brain = get_css_class
deprecated('css_class_from_brain',
           'Use get_css_class instead of css_class_from_brain')


css_class_from_obj = get_css_class
deprecated('css_class_from_obj',
           'Use get_css_class instead of css_class_from_obj')
