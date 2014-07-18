from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.dossier.behaviors.dossier import IDossierMarker
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import getMultiAdapter


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
