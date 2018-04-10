from ftw.upgrade.helpers import update_security_for
from opengever.base.model import create_session
from opengever.base.model.favorite import Favorite
from opengever.base.oguid import Oguid
from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent
from Products.CMFCore.CMFCatalogAware import CatalogAware
from sqlalchemy import and_
from zope.container.interfaces import IContainerModifiedEvent
from zope.lifecycleevent import IObjectRemovedEvent
from zope.sqlalchemy.datamanager import mark_changed


def object_moved_or_added(context, event):
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
        catalog = api.portal.get_tool('portal_catalog')
        catalog.reindexObject(context, idxs=CatalogAware._cmf_security_indexes,
                              update_metadata=0)


def remove_favorites(context, event):
    """Event handler which removes all existing favorites for the
    current context.
    """
    oguid = Oguid.for_object(context)

    stmt = Favorite.__table__.delete().where(Favorite.oguid == oguid)
    create_session().execute(stmt)


def is_title_changed(descriptions):
    for desc in descriptions:
        for attr in desc.attributes:
            if attr in ['IOpenGeverBase.title', 'title']:
                return True
    return False


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
        query.update({'title': context.title})

        mark_changed(create_session())
