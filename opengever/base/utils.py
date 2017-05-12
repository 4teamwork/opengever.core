from plone import api
from Products.CMFCore.utils import getToolByName
from xml.sax.saxutils import escape
from zope.component import getMultiAdapter
import json


def language_cache_key(method, context, request):
    """
    Generates cache key used for functions with different output depending on
    the current language.
    """
    portal_state = getMultiAdapter((context, request),
                                   name=u'plone_portal_state')
    key = "%s.%s:%s" % (method.__module__,
                        method.__name__,
                        portal_state.language())
    return key


def set_profile_version(portal, profile_id, version):
    """Set the DB version for a particular profile.

    (This function will be included in ftw.upgrade at some point.)
    """

    if profile_id.startswith('profile-'):
        raise Exception("Please specify the profile_id WITHOUT "
                        "the 'profile-' prefix!")

    if not len(profile_id.split(':')) == 2:
        raise Exception("Invalid profile id '%s'" % profile_id)

    ps = getToolByName(portal, 'portal_setup')
    ps.setLastVersionForProfile(profile_id, unicode(version))
    assert(ps.getLastVersionForProfile(profile_id) == (version, ))
    print "Set version for '%s' to '%s'." % (profile_id, version)
    return [version]


def ok_response(request=None):
    if request is None:
        request =  api.portal.get().REQUEST
    request.response.setHeader("Content-type", "text/plain")
    return 'OK'


def disable_edit_bar():
    api.portal.get().REQUEST.set('disable_border', True)


def get_preferred_language_code():
    ltool = api.portal.get_tool('portal_languages')
    language_code = ltool.getPreferredLanguage()

    # Special handling for combined languages, but works for regular ones too.
    return language_code.split('-')[0]


def get_hostname(request):
    """Extract hostname in virtual-host-safe manner

    @param request: HTTPRequest object, assumed contains environ dictionary

    @return: Host DNS name, as requested by client. Lowercased, no port part.
             Return None if host name is not present in HTTP request headers
             (e.g. unit testing).

    (from docs.plone.org/develop/plone/serving/http_request_and_response.html)
    """

    if "HTTP_X_FORWARDED_HOST" in request.environ:
        # Virtual host
        host = request.environ["HTTP_X_FORWARDED_HOST"]
    elif "HTTP_HOST" in request.environ:
        # Direct client request
        host = request.environ["HTTP_HOST"]
    else:
        return None

    # separate to domain name and port sections
    host = host.split(":")[0].lower()

    return host


def escape_html(text):
    """HTML escape a given string.

    See: https://wiki.python.org/moin/EscapingHtml
    """
    if text is None:
        return None

    # escape() and unescape() takes care of &, < and >, but not quotes
    html_escape_table = {
        '"': "&quot;",
        "'": "&apos;"
    }
    return escape(text, html_escape_table)


def pretty_json(obj):
    """Dump an object to a pretty printed JSON string.
    """
    return json.dumps(obj, indent=4, separators=(',', ': '))


def to_safe_html(markup):
    # keep empty data (whatever it is), it makes transform unhappy
    if not markup:
        return markup

    if not isinstance(markup, unicode):
        markup = markup.decode('utf-8')

    transformer = api.portal.get_tool('portal_transforms')
    return transformer.convert('safe_html', markup).getData()
