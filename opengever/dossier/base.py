
from Acquisition import aq_inner, aq_parent
from five import grok
from zope.component import queryMultiAdapter, queryUtility
from zope.interface import Interface

from plone.registry.interfaces import IRegistry
from plone.dexterity.content import Container
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFDefault.interfaces import ICMFDefaultSkin

from opengever.dossier.interfaces import IConstrainTypeDecider, IDossierContainerTypes
from opengever.dossier.behaviors.dossier import IDossierMarker

class DossierContainer( Container ):

    def allowedContentTypes( self, *args, **kwargs ):
        types = super(DossierContainer, self).allowedContentTypes(*args, **kwargs)
        # calculate depth
        depth = 0
        obj = self
        while IDossierMarker.providedBy( obj ):
            depth += 1
            obj = aq_parent( aq_inner( obj ) )
            if IPloneSiteRoot.providedBy( obj ):
                break
        # the adapter decides
        def filter_type( fti ):
            # first we try the more specific one ...
            decider = queryMultiAdapter( (self.REQUEST, self, fti),
                                    IConstrainTypeDecider,
                                    name=fti.portal_type)
            if not decider:
                # .. then we try the more general one
                decider = queryMultiAdapter( (self.REQUEST, self, fti),
                                        IConstrainTypeDecider)
            if decider:
                return decider.addable( depth )
            # if we don't have an adapter, we just allow it
            return True
        # filter
        return filter( filter_type, types )
        
    def show_subdossier(self):
        

        registry = queryUtility(IRegistry)
        reg_proxy = registry.forInterface(IDossierContainerTypes)
        depth = 0
        obj = self
        while IDossierMarker.providedBy( obj ):
            depth += 1
            obj = aq_parent( aq_inner( obj ) )
            if IPloneSiteRoot.providedBy( obj ):
                break
        if depth > getattr(reg_proxy, 'maximum_dossier_depth', 100):
            return False
        else:
            return True

class DefaultConstrainTypeDecider( grok.MultiAdapter ):
    grok.provides( IConstrainTypeDecider )
    grok.adapts(ICMFDefaultSkin, IDossierMarker, IDexterityFTI)
    grok.name( '' )

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


    def __init__( self, request, context, fti ):
        self.context = context
        self.request = request
        self.fti = fti

    def addable( self, depth ):
        container_type = self.context.portal_type
        factory_type = self.fti.id
        mapping = self.constrain_type_mapping
        for const_ctype, const_depth, const_ftype in mapping:
            if const_ctype==container_type and const_ftype==factory_type:
                return depth<const_depth or const_depth==0
        return True

    @property
    def constrain_type_mapping( self ):
        conf = DefaultConstrainTypeDecider.CONSTRAIN_CONFIGURATION
        for container_type, type_constr in conf.items():
            for factory_type, max_depth in type_constr.items():
                yield container_type, max_depth, factory_type

