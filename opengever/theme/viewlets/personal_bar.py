from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class PersonalBarViewlet(common.PersonalBarViewlet):

    """Personal bar viewlet showing the user portrait image.
    """
    index = ViewPageTemplateFile('personal_bar.pt')

    def portrait_url(self):
        mtool = getToolByName(self.context, 'portal_membership')
        portrait = mtool.getPersonalPortrait()
        if portrait is not None:
            return portrait.absolute_url()
        utool = getToolByName(self.context, 'portal_url')
        return '%s/defaultUser.png' % utool()
