## Script (Python) "require_login"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Login
##

from AccessControl import Unauthorized
from zExceptions import NotFound


portal = context.portal_url.getPortalObject()
portal_url = portal.absolute_url().rstrip('/') + '/'
request = context.REQUEST

if context.portal_membership.isAnonymousUser():
    return portal.restrictedTraverse('login')()

if request.method != 'GET':
    # We should not try to redirect when we have a POST payload,
    # because we cannot take along the payload.
    return portal.restrictedTraverse('insufficient_privileges')()


came_from_url = request.get('came_from')
if 'require_login_avoid_loop=' in came_from_url.split('?')[-1]:
    # We already sent the user back to the came_from url,
    # but it looks that we have a redirect loop due to an Unauthorized
    # exception while publishing the traversable endpoint.
    return portal.restrictedTraverse('insufficient_privileges')()
else:
    # Attach a marker so that we can detect redirect loops.
    if '?' in came_from_url:
        came_from_url += '&require_login_avoid_loop=true'
    else:
        came_from_url += '?require_login_avoid_loop=true'


if not came_from_url.startswith(portal_url):
    raise ValueError('URL {!r} not in portal {!r}'.format(
        came_from_url, portal_url))


came_from_path = came_from_url[len(portal_url):].split('?')[0].split('#')[0]
try:
    # Probe for an actual Unauthorized exception while traversing.
    portal.restrictedTraverse(came_from_path)
except Unauthorized:
    # This is expected to be the standard use case, where the user
    # actually has insufficient privileges.
    return portal.restrictedTraverse('insufficient_privileges')()
except (KeyError, AttributeError, NotFound):
    # The content could not be found.
    return portal.restrictedTraverse('insufficient_privileges')()
else:
    # We've had an Unauthorized exception on the previous resource although
    # the current user has enough privileges.
    # This usually because of an MS Office probe without cookies beforehand.
    # We simply redirect the user back to came_from for a retry.
    return request.RESPONSE.redirect(came_from_url)
