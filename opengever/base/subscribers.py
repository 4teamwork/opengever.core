from five import grok
from OFS.interfaces import IObjectClonedEvent
from opengever.base import _
from plone.app.lockingbehavior.behaviors import ILocking
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IEditBegunEvent
from plone.protect.interfaces import IDisableCSRFProtection
from zope.component.hooks import getSite
from zope.interface import alsoProvides


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


@grok.subscribe(ILocking, IEditBegunEvent)
def disable_plone_protect(obj, event):
    """Disables plone.protect for requests beginning an edit.
    Those requests cause the lockingbehavior to lock the content,
    which causes the transaction to be a write transaction.
    Since it is a GET request, plone.protect will disallow those requests
    unless we allow writes by disabling plone.protect.
    """
    alsoProvides(obj.REQUEST, IDisableCSRFProtection)
