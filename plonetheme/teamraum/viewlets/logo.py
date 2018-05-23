from BTrees.OOBTree import OOBTree
from plone.app.layout.viewlets import common
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import DEFAULT_STYLES
from plonetheme.teamraum.importexport import LOGO_KEY
from plonetheme.teamraum.importexport import LOGO_RIGHT_KEY
from plonetheme.teamraum.importexport import LOGO_TITLE_KEY
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LogoViewlet(common.LogoViewlet):

    index = ViewPageTemplateFile('logo.pt')

    def update(self):
        super(LogoViewlet, self).update()
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
