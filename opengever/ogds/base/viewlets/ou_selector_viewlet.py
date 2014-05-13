from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from five import grok
from opengever.ogds.base.utils import get_ou_selector
from plone.app.layout.viewlets import common
from zope.interface import Interface


class OrgUnitSelectorViewlet(common.ViewletBase):
    index = ViewPageTemplateFile('ou_selector_viewlet.pt')
    current_unit = None

    def get_active_unit(self):
        if not self.current_unit:
            self.current_unit = get_ou_selector().get_current_unit()
        return self.current_unit

    def get_units(self):
        return get_ou_selector().available_units()


class ChangeOrgUnitView(grok.View):
    grok.name('change_org_unit')
    grok.context(Interface)

    def render(self):

        unit_id = self.request.get('unit_id')

        if unit_id:
            get_ou_selector().set_current_unit(unit_id)

        return self.request.RESPONSE.redirect(self.context.absolute_url())
