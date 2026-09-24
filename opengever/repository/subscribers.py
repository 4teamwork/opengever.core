from opengever.bgtasks.task import queue_task
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.repository.interfaces import IDuringRepositoryDeletion
from opengever.repository.tasks import reindex_children_with_new_prefix
from opengever.repository.tasks import TASK_TYPE
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zExceptions import Forbidden
from zope.container.interfaces import IContainerModifiedEvent


def reindex_blocked_local_roles(repofolder, event):
    """Reindex blocked_local_roles upon the acquisition blockedness changing."""
    repofolder.reindexObject(idxs=['blocked_local_roles'])


def is_reference_number_prefix_changed(descriptions):
    for desc in descriptions:
        for attr in desc.attributes:
            if attr == 'IReferenceNumberPrefix.reference_number_prefix':
                return True
    return False


def update_reference_prefixes(obj, event):
    """A eventhandler which queues a background task to reindex all
    contained objects, if the reference prefix has been changed.
    """
    if ILocalrolesModifiedEvent.providedBy(event) or \
       IContainerModifiedEvent.providedBy(event):
        return

    if is_reference_number_prefix_changed(event.descriptions):
        admin_unit = get_current_admin_unit()
        if admin_unit is None:
            # OGDS not ready yet (e.g. setup/test contexts) - run inline.
            reindex_children_with_new_prefix(obj)
            return

        queue_task(TASK_TYPE, admin_unit.unit_id,
                   arguments={u'uid': obj.UID()})


def check_delete_preconditions(repository, event):
    """It's not allowed to delete repository folders or the repository root
    """

    # Ignore plone site deletions
    if IPloneSiteRoot.providedBy(event.object):
        return

    # Allow deletion done through the RepositoryDeleter
    if IDuringRepositoryDeletion.providedBy(event.object.REQUEST):
        return

    raise Forbidden('Deleting repository folders and roots is not allowed')
