from persistent.dict import PersistentDict
from persistent.list import PersistentList
from plone import api
from Products.CMFCore.utils import getToolByName
from xml.sax.saxutils import escape
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
import hashlib
import json


class NullObject(object):
    def __getattribute__(self, name):
        if name != '__dict__' and name not in self.__dict__:
            return lambda: u''
        return object.__getattribute__(self, name)

    def __iter__(self):
        yield u''
        for key in self.__dict__:
            yield key

    def __getitem__(self, key):
        return getattr(self, key)


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
        request = api.portal.get().REQUEST
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


def to_html_xweb_intelligent(text):
    """Transform input text to `text/x-web-intelligent`."""
    return (
        api.portal.get_tool(name='portal_transforms')
        .convertTo('text/html', text, mimetype='text/x-web-intelligent')
        .getData()
    )


def file_checksum(filename, chunksize=65536, algorithm=u'MD5'):
    """Calculates a checksum for the given file."""
    h = getattr(hashlib, algorithm.lower())()
    with open(filename, 'rb') as f:
        chunk = f.read(chunksize)
        while len(chunk) > 0:
            h.update(chunk)
            chunk = f.read(chunksize)
        return algorithm, h.hexdigest()


def make_persistent(data):
    """Recursively turn a nested data structure of lists and dicts
    into one using PersistentDics and PersistentLists.
    """
    if isinstance(data, dict):
        new = PersistentDict()
        for key, value in data.items():
            new[make_persistent(key)] = make_persistent(value)
        return new

    elif isinstance(data, list):
        new = PersistentList()
        for value in data:
            new.append(make_persistent(value))
        return new

    else:
        return data


def rewrite_path_list_to_absolute_paths(request):
    """If request contains a paths:list param, rewrite these paths so
    they're always absolute (start with the Plone site).

    (Modifies the request in place)

    This is required for a couple views that use a paths:list parameter and
    break with the new gever-ui, which sends "pseudo-relative" paths.

    Pseudo-relative in this context means paths that don't start with the
    Plone site (so are relative to it), but still have a leading slash).
    """
    if 'paths' in request:
        portal = getSite()
        portal_prefix = '/%s' % portal.id

        paths = request['paths']
        new_paths = []
        for path in paths:
            new_path = path

            if not path.startswith('/'):
                path = '/' + path

            if not path.startswith(portal_prefix):
                new_path = portal_prefix + path

            new_paths.append(new_path)

        request['paths'] = request.form['paths'] = new_paths


def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def is_administrator(user=None):
    """
    Returns a boolean indicating if the given user is considered a GEVER administrator.
    If no user is given, the current user is used.
    """
    if not user:
        user = api.user.get_current()
    return bool(user.has_role('Administrator') or user.has_role('Manager'))
