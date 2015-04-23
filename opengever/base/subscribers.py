from five import grok
from OFS.interfaces import IObjectClonedEvent
from opengever.base import _
from persistent.mapping import PersistentMapping
from plone.app.lockingbehavior.behaviors import ILocking
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IEditBegunEvent
from plone.protect.interfaces import IDisableCSRFProtection
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent
from zope.annotation import IAnnotations
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


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


@grok.subscribe(Interface, IUserLoggedOutEvent)
def disable_plone_protect_when_logging_out(user, event):
    """When logging out, the session is manipulated.
    This results in a lot of changes in the database, so we disable CSRF protection.
    """
    alsoProvides(user.REQUEST, IDisableCSRFProtection)


@grok.subscribe(IDexterityContent, IObjectCreatedEvent)
def initialize_annotations(obj, event):
    """We have to initalize the annotations on every object.
    To avoid CSRF protection messages on first access of newly created objects,
    which haven't accessed the annotations during the creation process.
    Because the PortletAssignment's, for example `ftw.footer` writes the
    PortletAssignments to the objects annotations.

    So if the annotations haven't been already accessed, the `AttributeAnnotations`
    mixin will create the `__annotations__` attribute on the object. This means that
    not the annotations are marked as changed but rather the object itself.

    And the we can't whitelist the object itself, because thats the important part
    of the CSRF protection.
    """

    annotations = IAnnotations(obj)
    annotations['initialized'] = True
    del annotations['initialized']
