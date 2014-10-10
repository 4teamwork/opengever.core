from AccessControl.SecurityManagement import newSecurityManager
from Products.CMFPlone.Portal import PloneSite
from Testing.makerequest import makerequest
from zope.app.component.hooks import setSite
import AccessControl


def get_first_plone_site(app):
    """Returns the first (of possibly many) Plone Site from a Zope application
    object. If no Plone sites are found an error is raised.
    """
    for item_id, item in sorted(app.items()):
        if isinstance(item, PloneSite):
            return app.unrestrictedTraverse(item_id)

    raise Exception("No Plone site found!")


def setup_plone(plone, options=None):
    """Takes care of setting up a request, manager security context and
    setting up the site manager for the given Plone site.
    Returns the Plone site root object.
    """
    app = plone.restrictedTraverse('/')

    # Set up request for debug / bin/instance run mode.
    app = makerequest(app)

    # Get a reference to the Plone site *inside* the request-wrapped app
    plone = app.restrictedTraverse(plone.id)

    # Set up Manager security context
    user = AccessControl.SecurityManagement.SpecialUsers.system
    user = user.__of__(app.acl_users)
    newSecurityManager(app, user)

    # Set up site to make component registry work
    setSite(plone)
    return plone
