from Acquisition import aq_inner, aq_parent
from five import grok
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.dossier import IDossierMarker
from opengever.dossier.interfaces import IConstrainTypeDecider, IDossierContainerTypes
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.interfaces import ICMFDefaultSkin
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from zope.component import queryMultiAdapter, queryUtility


class DossierContainer(Container):

    def allowedContentTypes(self, *args, **kwargs):
        types = super(DossierContainer, self).allowedContentTypes(*args, **kwargs)
        # calculate depth
        depth = 0
        obj = self
        while IDossierMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        # the adapter decides
        def filter_type(fti):
            # first we try the more specific one ...
            decider = queryMultiAdapter((self.REQUEST, self, fti),
                                    IConstrainTypeDecider,
                                    name=fti.portal_type)
            if not decider:
                # .. then we try the more general one
                decider = queryMultiAdapter((self.REQUEST, self, fti),
                                        IConstrainTypeDecider)
            if decider:
                return decider.addable(depth)
            # if we don't have an adapter, we just allow it
            return True
        # filter
        return filter(filter_type, types)

    def show_subdossier(self):
        registry = queryUtility(IRegistry)
        reg_proxy = registry.forInterface(IDossierContainerTypes)
        depth = 0
        obj = self
        while IDossierMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))
            if IPloneSiteRoot.providedBy(obj):
                break
        if depth > getattr(reg_proxy, 'maximum_dossier_depth', 100):
            return False
        else:
            return True

    def computeEndDate(self):
        """Compute a suggested end date for the (sub)dossier, based
        on the dates of its contained objects.

        The final end date is the date of the most recent object that's
        contained (directly or indirectly) in this dossier.
        """
        wft = getToolByName(self, 'portal_workflow')
        end_dates = []
        children = self.getChildNodes()
        for child in children:
            if child.portal_type == "opengever.document.document":
                end_dates.append(child.document_date)
            elif IDossierMarker.providedBy(child):
                end_dates.append(child.computeEndDate())

        # Remove dates that are 'None'
        end_dates = [d for d in end_dates if d]

        if end_dates:
            end_date = max(end_dates)
        else:
            review_state = wft.getInfoFor(self, 'review_state', None)
            # If a subdossier doesn't have documents, but has a (valid)
            # end date and has been resolved, use its end date
            if (IDossierMarker.providedBy(self)
            and review_state == 'dossier-state-resolved'
            and IDossier(self).end):
                return IDossier(self).end
            return None

        # Don't allow end_dates older than start_date
        if end_date < IDossier(self).start:
            end_date = IDossier(self).start
        return end_date


class DefaultConstrainTypeDecider(grok.MultiAdapter):
    grok.provides(IConstrainTypeDecider)
    grok.adapts(ICMFDefaultSkin, IDossierMarker, IDexterityFTI)
    grok.name('')

    CONSTRAIN_CONFIGURATION = {
        'opengever.dossier.businesscasedossier' : {
            'opengever.dossier.businesscasedossier' : 2,
            'opengever.dossier.projectdossier' : 1,
            },
        'opengever.dossier.projectdossier' : {
            'opengever.dossier.projectdossier' : 1,
            'opengever.dossier.businesscasedossier' : 1,
            },
        }


    def __init__(self, request, context, fti):
        self.context = context
        self.request = request
        self.fti = fti

    def addable(self, depth):
        container_type = self.context.portal_type
        factory_type = self.fti.id
        mapping = self.constrain_type_mapping
        for const_ctype, const_depth, const_ftype in mapping:
            if const_ctype==container_type and const_ftype==factory_type:
                return depth<const_depth or const_depth==0
        return True

    @property
    def constrain_type_mapping(self):
        conf = DefaultConstrainTypeDecider.CONSTRAIN_CONFIGURATION
        for container_type, type_constr in conf.items():
            for factory_type, max_depth in type_constr.items():
                yield container_type, max_depth, factory_type

