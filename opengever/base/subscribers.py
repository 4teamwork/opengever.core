from five import grok
from OFS.interfaces import IObjectClonedEvent
from opengever.base import _
from plone.dexterity.interfaces import IDexterityContent
from zope.component.hooks import getSite


@grok.subscribe(IDexterityContent, IObjectClonedEvent)
def create_initial_version(obj, event):
    """When a object was copied, create an initial version.
    """
    portal = getSite()
    pr = portal.portal_repository
    history = pr.getHistory(obj)

    if history is not None and not len(history) > 0:
        comment = _(u'label_initial_version_copied',
                    default="Initial version (document copied)")
        # Create an initial version
        pr._recursiveSave(obj, {}, pr._prepareSysMetadata(comment),
            autoapply=pr.autoapply)
