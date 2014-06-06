from Acquisition import aq_inner, aq_parent
from opengever.ogds.base.interfaces import IContactInformation
from opengever.ogds.base.utils import get_current_admin_unit
from plone.i18n.normalizer.interfaces import IIDNormalizer
from sqlalchemy.ext.declarative import DeclarativeMeta
from zope.component import getUtility


# XXX remove me
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


def _get_task_css_class(task):
    """A task helper function for `get_css_class`, providing some metadata
    of a task. The task may be a brain, a dexterity object or a sql alchemy
    globalindex object.
    """

    ### XXX: This method should be reworked complety!
    is_forwarding = False
    is_subtask = False
    predecessor_client = False
    admin_unit_id = False
    assigned_org_unit = False
    current_admin_unit = get_current_admin_unit()

    if isinstance(type(task), DeclarativeMeta):
        # globalindex
        predecessor_client = (task.predecessor and task.predecessor.admin_unit_id)
        assigned_org_unit = task.assigned_org_unit
        admin_unit_id = task.admin_unit_id
        is_subtask = task.is_subtask
        is_forwarding = task.task_type == 'forwarding_task_type'

    elif hasattr(task, 'is_subtask'):
        # catalog brain
        predecessor_client = (
            task.predecessor and task.predecessor.split(':')[0])
        admin_unit_id = task.client_id
        assigned_org_unit = task.assigned_client

        is_subtask = task.is_subtask
        is_forwarding = (task.portal_type == 'opengever.inbox.forwarding')

    else:
        # dexterity object
        predecessor_client = (
            task.predecessor and task.predecessor.split(':')[0])
        admin_unit_id = current_admin_unit.id()
        assigned_org_unit = task.responsible_client

        is_subtask = (
            aq_parent(aq_inner(task)).portal_type == 'opengever.task.task')
        is_forwarding = (task.portal_type == 'opengever.inbox.forwarding')

    # is it a remote task?
    if predecessor_client and predecessor_client != assigned_org_unit:
        is_remote = True
    elif admin_unit_id != assigned_org_unit:
        is_remote = True
    else:
        is_remote = False

    # choose class
    if is_forwarding:
        return 'contenttype-opengever-inbox-forwarding'

    elif is_subtask and is_remote:
        if admin_unit_id == current_admin_unit.id():
            return 'icon-task-subtask'
        else:
            return 'icon-task-remote-task'

    elif is_subtask:
        return 'icon-task-subtask'

    elif is_remote:
        return 'icon-task-remote-task'

    else:
        return 'contenttype-opengever-task-task'


def get_css_class(item):
    """Returns the content-type icon css class for `item`.

    Arguments:
    `item` -- obj or brain
    """

    css_class = None

    normalize = getUtility(IIDNormalizer).normalize
    if isinstance(type(item), DeclarativeMeta) or \
            item.portal_type == 'opengever.task.task':

        return _get_task_css_class(item)

    elif item.portal_type == 'opengever.document.document':
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

    if css_class is None:
        css_class = "contenttype-%s" % normalize(item.portal_type)

    return css_class
