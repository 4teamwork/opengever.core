from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ENABLED
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from opengever.repository.interfaces import IRepositoryFolder
from opengever.repository.interfaces import IRepositoryFolderRecords
from plone.memoize.view import memoize_contextless
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import queryUtility
from zope.globalrequest import getRequest
from zope.interface import implements


class RepositoryFolderConstrainTypes(object):
    """Restrict addable types for repository folders.
    """
    implements(IConstrainTypes)
    adapts(IRepositoryFolder)

    def __init__(self, context):
        self.context = context
        self.request = getRequest()

    def getConstrainTypesMode(self):
        """Find out if add-restrictions are enabled."""
        # Allow types from locallyAllowedTypes only
        return ENABLED

    def getLocallyAllowedTypes(self):
        """Return the list of FTI ids for the types which should be allowed to
           be added in this container.
        """
        return [t.getId() for t in self.allowedContentTypes()]

    def getImmediatelyAddableTypes(self):
        """Return a subset of the FTI ids from getLocallyAllowedTypes() which
           should be made most easily available.
        """
        return self.getLocallyAllowedTypes()

    def getDefaultAddableTypes(self):
        """Return a list of FTIs which correspond to the list of FTIs available
           when the constraint mode = 0 (that is, the types addable without any
           setLocallyAllowedTypes trickery involved)
        """
        # Copied from plone.app.dexterity.behaviors.constrains
        portal_types = getToolByName(self.context, 'portal_types')
        my_type = portal_types.getTypeInfo(self.context)
        result = portal_types.listTypeInfo()
        return [t for t in result if my_type.allowType(t.getId()) and
                t.isConstructionAllowed(self.context)]

    @memoize_contextless
    def allowedContentTypes(self):
        """Return the list of currently permitted FTIs."""

        # We have to follow some rules:
        # 1. If this RepositoryFolder contains another RF, we should not be
        # able to add other types than RFs.
        # 2. If we are reaching the maximum depth of repository folders
        # (Configured in plone.registry), we should not be able to add
        # any more RFs, but then we should be able to add the other configured
        # types in any case. If the maximum_repository_depth is set to 0,
        # we do not have a depth limit.

        types = self.getDefaultAddableTypes()
        fti = self.context.getTypeInfo()

        # Get maximum depth of repository folders
        registry = queryUtility(IRegistry)
        proxy = registry.forInterface(IRepositoryFolderRecords)
        # 0 -> no restriction
        maximum_depth = getattr(proxy, 'maximum_repository_depth', 0)
        current_depth = 0
        # If we have a maximum depth, we need to know the current depth
        if maximum_depth > 0:
            obj = self.context
            while IRepositoryFolder.providedBy(obj):
                current_depth += 1
                obj = aq_parent(aq_inner(obj))
                if IPloneSiteRoot.providedBy(obj):
                    break
            if maximum_depth <= current_depth:
                # Depth exceeded
                # RepositoryFolder not allowed, but any other type
                types = filter(lambda a: a != fti, types)

        # Filter content types, if required
        if not self.context.is_leaf_node():
            # only allow same types, except dispositions
            types = filter(
                lambda a: a == fti or a.id == 'opengever.disposition.disposition',
                types)

        # Finally: remove not enabled resticted content types
        marker_behavior = 'opengever.dossier.behaviors.restricteddossier.' + \
            'IRestrictedDossier'

        allowed = self.context.addable_dossier_types \
            and self.context.addable_dossier_types or []

        def _filterer(fti):
            if fti.id in allowed:
                # FTI is enabled in repository folder
                return True

            elif getattr(fti, 'behaviors', None) \
                    and marker_behavior in fti.behaviors:
                # FTI has marker interface and is not enabled
                return False

            else:
                # Normal type - we don't care
                return True

        types = filter(_filterer, types)

        return types
