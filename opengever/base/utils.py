from Acquisition import aq_inner
from Acquisition import aq_parent
from App.config import DefaultConfiguration
from opengever.dossier.behaviors.dossier import IDossierMarker
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getMultiAdapter
import App.config
import os


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


def find_parent_dossier(content):
    """Returns the first parent dossier relative to the current context.
    """

    if IPloneSiteRoot.providedBy(content):
        raise ValueError('Site root passed as argument.')

    while not IDossierMarker.providedBy(content):
        content = aq_parent(aq_inner(content))
        if IPloneSiteRoot.providedBy(content):
            raise ValueError('Site root reached while searching '
                             'parent dossier.')
    return content


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


class PathFinder(object):
    """Helper class to provide various Zope2 Instance related paths that are
    otherwise cumbersone to access.
    """

    def __init__(self):
        self._assert_proper_configuration()
        self._instance_home = os.environ['INSTANCE_HOME']
        self._client_home = os.environ['CLIENT_HOME']

    def _assert_proper_configuration(self):
        cfg = App.config._config
        if cfg is None or isinstance(cfg, DefaultConfiguration):
            raise RuntimeError(
                "Zope is not configured properly yet, refusing "
                "operate on paths that might be wrong!")

    @property
    def var(self):
        """Path to {buildout}/var
        """
        return os.path.normpath(os.path.join(self._client_home, '..'))

    @property
    def var_log(self):
        """Path to {buildout}/var/log
        """
        return os.path.join(self.var, 'log')

    @property
    def buildout(self):
        """Path to {buildout}
        """
        return os.path.normpath(os.path.join(self.var, '..'))


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
