from opengever.base.config_checks.manager import ConfigCheckManager
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ConfigCheckViewlet(ViewletBase):

    index = ViewPageTemplateFile('config_check.pt')

    def errors(self):
        return ConfigCheckManager().check_all()
