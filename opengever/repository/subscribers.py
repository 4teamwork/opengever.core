from plone import api
from plone.app.workflow.interfaces import ILocalrolesModifiedEvent


def is_reference_number_prefix_changed(descriptions):
    for desc in descriptions:
        for attr in desc.attributes:
            if attr == 'IReferenceNumberPrefix.reference_number_prefix':
                return True
    return False


def update_reference_prefixes(obj, event):
    """A eventhandler which reindex all contained objects, if the
    reference prefix has been changed.
    """
    if ILocalrolesModifiedEvent.providedBy(event):
        return

    if is_reference_number_prefix_changed(event.descriptions):
        catalog = api.portal.get_tool('portal_catalog')
        children = catalog.unrestrictedSearchResults(
            path='/'.join(obj.getPhysicalPath()))
        for child in children:
            child.getObject().reindexObject(idxs=['reference'])
