from Products.CMFCore.utils import getToolByName
from Products.CMFEditions.interfaces.IArchivist import ArchivistUnregisteredError
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError
from Products.CMFPlone.utils import base_hasattr
from five import grok
from opengever.document import _
from opengever.document.document import IDocumentSchema
from zope.app.container.interfaces import IObjectAddedEvent
from opengever.task.util import CUSTOM_INITIAL_VERSION_MESSAGE


# A special Attribute for the migration
MIGRATION = False


@grok.subscribe(IDocumentSchema, IObjectAddedEvent)
def create_initial_version(context, event):
    """Event handler which creates a initial version when adding a new document.
    Since we use manual versioning for the document, the initial version doesn't
    get created automatically.
    """
    # A special Attribute for the migration
    # The inital version shouldn't set passing the migration
    # TODO: After the migration it should be removed

    if MIGRATION:
        return

    if context.portal_factory.isTemporary(context):
        # don't do anything if we're in the factory
        return

    pr = getToolByName(context, 'portal_repository')
    if not pr.isVersionable(context):
        # object is not versionable
        return

    if context.REQUEST.get(CUSTOM_INITIAL_VERSION_MESSAGE, None):
        change_note = context.REQUEST.get(CUSTOM_INITIAL_VERSION_MESSAGE)
    else:
        change_note = _(u'initial_document_version_change_note',
                    default=u'Initial version')

    changed = False
    if not base_hasattr(context, 'version_id'):
        # no initial version, let's create one..
        changed = True

    else:
        try:
            changed = not pr.isUpToDate(context, context.version_id)
        except ArchivistUnregisteredError:
            # The object is not actually registered, but a version is
            # set, perhaps it was imported, or versioning info was
            # inappropriately destroyed
            changed = True

    if not changed:
        return

    try:
        context.portal_repository.save(obj=context, comment=change_note)
    except FileTooLargeToVersionError:
        pass # the on edit save will emit a warning
