from AccessControl import Unauthorized
from AccessControl.SecurityManagement import getSecurityManager
from Acquisition import aq_parent
from five import grok
from ftw.tabbedview.browser.tabbed import TabbedView
from plone.app.lockingbehavior.behaviors import ILocking
from plone.app.relationfield.event import extract_relations
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IEditBegunEvent
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.interfaces import ISiteRoot
from Products.PluggableAuthService.interfaces.events import IUserLoggedOutEvent
from z3c.relationfield.event import _setRelation
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from ZPublisher.interfaces import IPubAfterTraversal


ALLOWED_ENDPOINTS = set([
    'POST_application_json_@login',
    'POST_application_json_@logout',
    'POST_application_json_@login-renew',
    'customlogo',
    'customlogo_right',
    'favicon',
    'list-open-dossiers-json',
    'logged_out',
    'login',
    'login_failed',
    'login_form',
    'logout',
    'mail-inbound',
    'mail_password',
    'mail_password_form',
    'mnt-warmup',
    'passwordreset',
    'pwreset_finish',
    'pwreset_form',
    'require_login',
    'update_sync_stamp',
    'watcher-feed',
    'zauth',
    'bumblebee_download',
    'health-check',
])


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


@grok.subscribe(IDexterityContent, IObjectAddedEvent)
def add_behavior_relations(obj, event):
    """Register relations in behaviors.

    This event handler fixes a bug in plone.app.relationfield, which only
    updates the zc.catalog when an object gets modified, but not when it gets
    added.
    """
    for behavior_interface, name, relation in extract_relations(obj):
        _setRelation(obj, name, relation)


@grok.subscribe(IPubAfterTraversal)
def disallow_anonymous_views_on_site_root(event):
    """Do not allow access for anonymous to views on the portal root except
       those explicitly allowed here. We do it this way because we cannot
       revoke the view permissions for anonymous on the portal root.

       The same applies for tabbed_view attributes of a tabbed_view that is
       displayed for the portal root.
    """
    user = getSecurityManager().getUser()
    if user is None or user.getUserName() == 'Anonymous User':
        context = event.request['PARENTS'][0]

        is_site_root = ISiteRoot.providedBy(context)
        is_tabbed_view_on_site_root = isinstance(context, TabbedView) and \
            ISiteRoot.providedBy(aq_parent(context))

        if is_site_root or is_tabbed_view_on_site_root:
            endpoint_name = event.request['PUBLISHED'].__name__
            if endpoint_name not in ALLOWED_ENDPOINTS:
                raise Unauthorized
