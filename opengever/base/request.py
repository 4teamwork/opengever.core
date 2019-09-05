from opengever.base.sentry import maybe_report_exception
from opengever.ogds.base.exceptions import ClientNotFound
from opengever.ogds.base.interfaces import IInternalOpengeverRequestLayer
from opengever.ogds.base.utils import get_current_admin_unit
from opengever.ogds.base.utils import ogds_service
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from ZODB.POSException import ConflictError
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.globalrequest import getRequest
from zope.interface import alsoProvides
import json
import os.path
import sys
import traceback
import urllib
import urllib2


class RemoteRequestFailed(Exception):
    """Exception class for remote requests"""

    def __init__(self, url, tb):
        self.url = url
        self.tb = tb

    def __str__(self):
        return 'Remote request to "{url}" failed: Traceback: {tb}'.format(
            **{'url': self.url, 'tb': self.tb})


def dispatch_json_request(target_admin_unit_id, viewname, path='',
                          data={}, headers={}):
    """ Sends a request to a json-action on a remote zope instance,
    decodes the response with json and returns it.

    :target_admin_unit_id: id of the target AdminUnit
    :viewname: name of the view to call on the target
    :path: context path relative to site root
    :data: dict of additional data to send
    :headers: dict of additional headers to send
    """

    response = dispatch_request(target_admin_unit_id, viewname, path=path,
                                data=data, headers=headers)
    data = response.read()
    return json.loads(data)


def expect_ok_response(response, msg="Unexpected response {!r}"):
    response_body = response.read()
    if response_body != 'OK':
        raise ValueError(msg.format(response_body))
    return response


def dispatch_request(target_admin_unit_id, viewname, path='',
                     data={}, headers={}):
    """ Sends a request to another zope instance Returns a response stream

    Authentication:
    In the request there is a attribute '__cortex_ac' which is set to the
    username of the current user.

    :target_admin_unit_id: id of the target AdminUnit
    :viewname: name of the view to call on the target
    :path: context path relative to site root
    :data: dict of additional data to send
    :headers: dict of additional headers to send
    """

    if isinstance(viewname, unicode):
        viewname = viewname.encode('utf-8')
    if isinstance(path, unicode):
        path = path.encode('utf-8')

    if get_current_admin_unit().id() == target_admin_unit_id:
        return _local_request(viewname, path, data)
    else:
        return _remote_request(target_admin_unit_id, viewname, path,
                               data, headers)


def _local_request(viewname, path, data):
    # do not connect to the site itself but do a restrictedTraverse
    request = getRequest()
    alsoProvides(request, IInternalOpengeverRequestLayer)
    site = getSite()

    # we need to back up the request data and set them new for the
    # view which is called with the same request (restrictedTraverse)
    ori_form = request.form
    ori_other = request.other
    request.form = data
    request.other = ori_other.copy()
    for key in ori_form.keys():
        if key in request.other:
            del request.other[key]

    # kss validation overrides getSite() hook with a bad object
    # but we need getSite to work properly, so we fix it.
    old_site = None
    if site.__class__.__name__ == 'Z3CFormValidation':
        old_site = site
        fixed_site = getToolByName(site, 'portal_url').getPortalObject()
        setSite(fixed_site)

    site = getSite()
    if path:
        view = site.unrestrictedTraverse(os.path.join(path, viewname))
    else:
        view = site.unrestrictedTraverse(viewname)
    data = view()

    if old_site:
        # Restore the site if necessary
        site = old_site
        setSite(site)

    # restore the request
    request.form = ori_form
    request.other = ori_other

    return StringIO(data)


def _remote_request(target_admin_unit_id, viewname, path, data, headers):
    site = getSite()
    target_unit = ogds_service().fetch_admin_unit(target_admin_unit_id)

    if not target_unit:
        raise ClientNotFound()

    headers = headers.copy()
    data = data.copy()

    mtool = getToolByName(site, 'portal_membership')
    member = mtool.getAuthenticatedMember()

    key = 'X-OGDS-AC'
    if key not in headers.keys() and member:
        headers[key] = member.getId()

    headers['X-OGDS-AUID'] = get_current_admin_unit().id()
    handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(handler)

    viewname = viewname if viewname.startswith(
        '@@') else '@@{}'.format(viewname)
    if path:
        url = os.path.join(target_unit.site_url, path, viewname)
    else:
        url = os.path.join(target_unit.site_url, viewname)

    request = urllib2.Request(url,
                              urllib.urlencode(data),
                              headers)

    response = opener.open(request)
    content = response.read().strip()

    if response.headers.type == 'text/x.traceback':
        raise RemoteRequestFailed(url, content)
    else:
        return StringIO(content)


def tracebackify(*args, **kwargs):
    """Decorator for remote endpoints
    The decorator safely calls the View and returns the traceback as string.
    Plus: Also try to report the traceback to sentry, so the original
    traceback from the remote view is reported too"""

    to_re_raise = kwargs.pop('to_re_raise', None)

    if not isinstance(to_re_raise, list):
        to_re_raise = [to_re_raise]

    def wrapper(Cls):

        class SafeCall(Cls):
            def __call__(self, *args, **kwargs):

                try:
                    return super(SafeCall, self).__call__(*args, **kwargs)
                except (ConflictError, KeyboardInterrupt):
                    raise
                except tuple(to_re_raise):
                    raise
                except Exception:
                    self.request.response.setHeader("Content-type",
                                                    "text/x.traceback")
                    e_type, e_value, tb = sys.exc_info()

                    maybe_report_exception(self.context, self.request,
                                           e_type, e_value, tb)

                    return ''.join(traceback.format_exception(e_type, e_value,
                                                              tb))
        return SafeCall

    if args:
        Cls = args[0]
        return wrapper(Cls)
    else:
        def decorator(Cls):
            return wrapper(Cls)
        return decorator
