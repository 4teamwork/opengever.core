from borg.localrole.interfaces import IFactoryTempFolder
from BTrees.OOBTree import OOBTree
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets import common
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import DEFAULT_STYLES
from plonetheme.teamraum.importexport import LOGO_KEY
from plonetheme.teamraum.importexport import LOGO_RIGHT_KEY
from plonetheme.teamraum.importexport import LOGO_TITLE_KEY
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import pkg_resources


try:
    pkg_resources.get_distribution('ftw.subsite')
except pkg_resources.DistributionNotFound:
    HAS_SUBSITE = False
else:
    from ftw.subsite.interfaces import IFtwSubsiteLayer
    HAS_SUBSITE = True


class LogoViewlet(common.LogoViewlet):

    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()

        if HAS_SUBSITE and IFtwSubsiteLayer.providedBy(self.request):
            self.subsite_logo_behaviour()
        else:
            self.teamraum_logo_behaviour()

    def teamraum_logo_behaviour(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        customstyles_util = CustomStylesUtility(portal)
        customstyles = customstyles_util.annotations.get(
            'customstyles', OOBTree(DEFAULT_STYLES))
        url = "%s/++theme++plonetheme.teamraum/images/logo_teamraum.png" % \
            portal.absolute_url()

        if LOGO_KEY in customstyles and customstyles[LOGO_KEY]:
            url = "%s/customlogo" % portal.absolute_url()
        self.logo_tag = "<img src='%s' alt='%s Logo' />" % (
            url,
            portal.Title())

        self.logo_title = ''
        if LOGO_TITLE_KEY in customstyles:
            self.logo_title = customstyles[LOGO_TITLE_KEY]

    def subsite_logo_behaviour(self):
        # Copy of ftw.subsite.viewlets.subsitelogoviewlet
        portal = self.portal_state.portal()
        self.navigation_root_url = self.portal_state.navigation_root_url()

        subsite_logo = getattr(self.context, 'getLogo', None)
        in_factory = IFactoryTempFolder.providedBy(
            self.context.aq_inner.aq_parent)

        if subsite_logo and subsite_logo() and not in_factory:
            # we are in a subsite
            navigation_root_path = self.portal_state.navigation_root_path()
            scale = portal.restrictedTraverse(
                navigation_root_path + '/@@images')
            self.logo_tag = scale.scale('logo', scale="mini").tag()
            self.title = self.context.restrictedTraverse(
                getNavigationRoot(self.context)).Title()
            # On subsites we do not have a customizable logo title
            self.logo_title = ''
        else:
            # teamraum default
            self.teamraum_logo_behaviour()


class LogoRightViewlet(common.LogoViewlet):

    index = ViewPageTemplateFile('logo_right.pt')

    def update(self):
        super(LogoRightViewlet, self).update()

        self.teamraum_logo_behaviour()

    def teamraum_logo_behaviour(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        customstyles_util = CustomStylesUtility(portal)
        customstyles = customstyles_util.annotations.get(
            'customstyles', OOBTree(DEFAULT_STYLES))
        url = "%s/++theme++plonetheme.teamraum/images/logo_teamraum.png" % \
            portal.absolute_url()

        if LOGO_RIGHT_KEY in customstyles and customstyles[LOGO_RIGHT_KEY]:
            url = "%s/customlogoright" % portal.absolute_url()
        self.logo_tag = "<img src='%s' alt='%s Logo' />" % (
            url,
            portal.Title())
