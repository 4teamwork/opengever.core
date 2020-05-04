from Acquisition._Acquisition import aq_parent
from DateTime import DateTime
from ftw.upgrade.helpers import update_security_for
from opengever.base.behaviors.changed import IChanged
from opengever.base.date_time import utcnow_tz_aware
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from opengever.base.security import reindex_object_security_without_children
from opengever.base.touched import ObjectTouchedEvent
from opengever.base.touched import should_track_touches
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.indexers import TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX
from opengever.globalindex.handlers.task import sync_task
from opengever.repository.interfaces import IRepositoryFolder
from opengever.task.task import ITask
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFPlone.interfaces import IPloneSiteRoot
from sqlalchemy import and_
from zope.container.interfaces import IContainerModifiedEvent
from zope.event import notify
from zope.lifecycleevent import IObjectRemovedEvent
from zope.lifecycleevent import ObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectMovedEvent
from zope.sqlalchemy.datamanager import mark_changed


reindex_after_copy = ['created']


def object_copied(context, event):
    context.creation_date = DateTime()
    context._v_object_has_been_copied = True


def object_moved_or_added(context, event):
    if isinstance(event, ObjectAddedEvent):
        # Don't consider moving or removing an object a "touch". Mass-moves
        # would immediately fill up the touched log, and removals should not
        # be tracked anyway.
        if should_track_touches(context):
            notify(ObjectTouchedEvent(context))

        # If an object has been copy & pasted, we need to reindex some fields.
        # The IObjectCopiedEvent is too early to do that though, because at
        # that point the object doesn't have a full AQ chain yet. We therefore
        # just mark it during IObjectCopiedEvent, and do the reindexing here.
        if getattr(context, '_v_object_has_been_copied', False):
            context.reindexObject(idxs=reindex_after_copy)

    if IObjectRemovedEvent.providedBy(event):
        return

    # Update object security after moving or copying.
    # Specifically, this is needed for the case where an object is moved out
    # of a location where a Placeful Workflow Policy applies to a location
    # where it doesn't.
    #
    #  Plone then no longer provides the placeful workflow for that object,
    # but doesn't automatically update the object's security.
    #
    # We use ftw.upgrade's update_security_for() here to correctly
    # recalculate security, but do the reindexing ourselves because otherwise
    # Plone will do it recursively (unnecessarily so).
    changed = update_security_for(context, reindex_security=False)
    if changed:
        reindex_object_security_without_children(context)

    # There are several indices that need updating when a dossier is moved.
    # first make sure obj was actually moved and not created
    if not event.oldParent or not event.newParent:
        return

    # When an object is moved, its containing_dossier needs reindexing.
    to_reindex = ['containing_dossier']
    # containing_subdossier is really only used for documents,
    # while is_subdossier is only meaningful for dossiers.
    if IDossierMarker.providedBy(context):
        was_subdossier = IDossierMarker.providedBy(event.oldParent)
        is_subdossier = IDossierMarker.providedBy(event.newParent)
        if was_subdossier != is_subdossier:
            to_reindex.append('is_subdossier')

    if IDossierMarker.providedBy(context) and IObjectMovedEvent.providedBy(event):
        # The moved dossier may change from a dossier to a subdossier or vice-versa.
        Favorite.query.update_is_subdossier(context)

    if IRepositoryFolder.providedBy(context) and IObjectMovedEvent.providedBy(event):
        # The moved repository folder may change from a branch node to a leaf
        # node or vice-versa.
        Favorite.query.update_is_leafnode(context)

        # Its old and new parent may also change from a branch node to a leaf
        # node or vice-versa.
        Favorite.query.update_is_leafnode(event.oldParent)
        Favorite.query.update_is_leafnode(event.newParent)

    if context.portal_type in TYPES_WITH_CONTAINING_SUBDOSSIER_INDEX:
        to_reindex.append('containing_subdossier')

    context.reindexObject(idxs=to_reindex)

    # synchronize with model if necessary
    if ITask.providedBy(context):
        sync_task(context, event)


def remove_favorites(context, event):
    """Event handler which removes all existing favorites for the
    current context.
    """

    # Skip plone site removals. Unfortunately no deletion-order seems to be
    # guaranteed, when removing the plone site, so it might happen that the
    # intid utility is removed before removing content.
    if IPloneSiteRoot.providedBy(event.object):
        return

    oguid = Oguid.for_object(context)

    stmt = Favorite.__table__.delete().where(Favorite.oguid == oguid)
    create_session().execute(stmt)


def is_title_changed(descriptions):
    for desc in descriptions:
        for attr in desc.attributes:
            if attr in ['IOpenGeverBase.title', 'title']:
                return True
    return False


def object_modified(context, event):
    update_favorites_title(context, event)

    if should_track_touches(context):
        notify(ObjectTouchedEvent(context))


def update_favourised_repositoryfolder(context, event):
    # A favourised leaf repository folder becomes a branch node when a
    # child repository folder is added.
    # A favourised branch node becomes a leaf node when the last same
    # type child has been removed.
    Favorite.query.update_is_leafnode(aq_parent(context))


def update_favorites_review_state(context, event):
    # Workflow transactions must trigger the update of the associated favourites.
    Favorite.query.update_review_state(context)


def update_favorites_title(context, event):
    """Event handler which updates the titles of all existing favorites for the
    current context, unless the title is personalized.
    """
    if IContainerModifiedEvent.providedBy(event):
        return

    if ILocalrolesModifiedEvent.providedBy(event):
        return

    if is_title_changed(event.descriptions):
        query = Favorite.query.filter(
            and_(Favorite.oguid == Oguid.for_object(context),
                 Favorite.is_title_personalized == False))  # noqa
        query.update_title(context.title)

        mark_changed(create_session())


"""
The 'changed' field is updated when an object is created
(IObjectAddedEvent) and generally when modified by a user
(IObjectModifiedEvent except when the object is simply reindexed).
The field is also updated for workflow status changes and when a document
is checked-in or reverted to an older version. See opengever/base/configure.zcml
for registered events handled by the 'maybe_update_changed_date' and
'update_changed_date' handlers.
"""
EVENTS_NOT_UPDATING_CHANGED = (IContainerModifiedEvent, ILocalrolesModifiedEvent)


def maybe_update_changed_date(context, event):
    for interface in EVENTS_NOT_UPDATING_CHANGED:
        if interface.providedBy(event):
            return
    update_changed_date(context, event)


def update_changed_date(context, event):
    IChanged(context).changed = utcnow_tz_aware()
    context.reindexObject(idxs=["changed"])
