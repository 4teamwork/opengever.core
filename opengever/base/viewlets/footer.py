from pkg_resources import get_distribution
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize import forever
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FooterViewlet(ViewletBase):

    index = ViewPageTemplateFile('footer.pt')

    @forever.memoize
    def get_gever_version(self):
        return '2019.3.4'
