from AccessControl import getSecurityManager
from AccessControl import Unauthorized
from AccessControl.users import nobody
from OFS.interfaces import IItem
from plone.app.relationfield.event import extract_relations
from plone.protect.interfaces import IDisableCSRFProtection
from Products.CMFCore.interfaces import ISiteRoot
from z3c.relationfield.event import _setRelation
from zope.annotation import IAnnotations
from zope.interface import alsoProvides
from zope.publisher.interfaces.browser import IBrowserView


ALLOWED_ENDPOINTS = set([
    'GET_application_json_@config',
    'GET_application_json_@dossier-transfers',
    'GET_application_json_@white-labeling-settings',
    'POST_application_json_@caslogin',
    'POST_application_json_@login',
    'POST_application_json_@logout',
    'POST_application_json_@login-renew',
    'customlogo',
    'customlogo_right',
    'dump-content-stats',
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
    'upgrades-api',
    'oauth2-token',
    'my-invitations',
    'wopi',
])

BASIC_AUTH_ENDPOINTS = [
    'POST_application_json_@scan-in'
]


def disable_plone_protect(obj, event):
    """Disables plone.protect for requests beginning an edit.
    Those requests cause the lockingbehavior to lock the content,
    which causes the transaction to be a write transaction.
    Since it is a GET request, plone.protect will disallow those requests
    unless we allow writes by disabling plone.protect.
    """
    alsoProvides(obj.REQUEST, IDisableCSRFProtection)


def disable_plone_protect_when_logging_out(user, event):
    """When logging out, the session is manipulated.
    This results in a lot of changes in the database, so we disable CSRF protection.
    """
    alsoProvides(user.REQUEST, IDisableCSRFProtection)


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


def add_behavior_relations(obj, event):
    """Register relations in behaviors.

    This event handler fixes a bug in plone.app.relationfield, which only
    updates the zc.catalog when an object gets modified, but not when it gets
    added.
    """
    for behavior_interface, name, relation in extract_relations(obj):
        _setRelation(obj, name, relation)


def disallow_anonymous_views_on_site_root(event):
    """Do not allow access for anonymous to views on the portal root except
       those explicitly allowed here. We do it this way because we cannot
       revoke the view permissions for anonymous on the portal root.

       The same applies for tabbed_view attributes of a tabbed_view that is
       displayed for the portal root.

       In addition, disallow access to member portraits for Anonymous users.
    """
    if getSecurityManager().getUser() != nobody:
        return

    # Block anonymous access to member portraits
    if '/portal_memberdata/portraits/' in event.request.getURL():
        raise Unauthorized

    # Find the first physical / persistent object in the PARENTS
    # by filtering all non-persist parents (views, widgets, ...).
    context = filter(IItem.providedBy, event.request['PARENTS'])[0]
    if not ISiteRoot.providedBy(context):
        return

    endpoint_name = event.request['PUBLISHED'].__name__
    if endpoint_name in ALLOWED_ENDPOINTS:
        return

    views = filter(IBrowserView.providedBy, event.request['PARENTS'])
    if len(views) > 0 and views[0].__name__ in ALLOWED_ENDPOINTS:
        return

    if endpoint_name in BASIC_AUTH_ENDPOINTS:
        event.request.response['WWW-Authenticate'] = 'Basic'

    raise Unauthorized


def scrub_server_version(event):
    """Scrub the server version string response headers."""
    if getattr(event, 'request', None):
        if getattr(event.request, 'RESPONSE', None):
            if getattr(event.request.RESPONSE, '_server_version', None):
                event.request.RESPONSE._server_version = 'Zope'


def set_security_headers(event):
    """Set headers related to security"""
    response = getattr(getattr(event, 'request', None), 'response', None)
    if response is not None:
        content_type = response.headers.get('content-type', None)

        # Do not set any headers if the response doesn't have a content type
        # This is e.g. the case for 304 not modified responses.
        if content_type is None:
            return

        # Only load scripts and stylesheets with the correct content type
        response.setHeader('X-Content-Type-Options', 'nosniff')

        # Enable browser protection for reflected XSS attacks
        response.setHeader('X-XSS-Protection', '1; mode=block')

        # Keep existing CSP header to allow browser views to set a custom CSP
        if response.getHeader('Content-Security-Policy') is None:
            if content_type.startswith('text/html'):
                # Allow resources from current origin, eval, inline js and css
                # Allow images from current origin and data urls
                # Disallow plugins and framing
                response.setHeader(
                    'Content-Security-Policy',
                    "default-src 'self' 'unsafe-eval' 'unsafe-inline'; "
                    "img-src 'self' data:; "
                    "object-src 'none'; frame-ancestors 'none'")
            else:
                # Disallow the loading of any resources and disable framing
                response.setHeader(
                    'Content-Security-Policy',
                    "default-src 'none'; frame-ancestors 'none'")

        # Only send referrer on requests to the same origin
        response.setHeader('Referrer-Policy', 'same-origin')
