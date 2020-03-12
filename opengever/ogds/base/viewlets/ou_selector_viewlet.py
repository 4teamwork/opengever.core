from opengever.ogds.base.utils import get_ou_selector
from opengever.ogds.models.service import ogds_service
from plone.app.caching.interfaces import IETagValue
from plone.app.layout.viewlets import common
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from sqlalchemy.exc import OperationalError
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
import logging


logger = logging.getLogger('opengever.ogds.base')


class OrgUnitSelectorViewlet(common.ViewletBase):
    index = ViewPageTemplateFile('ou_selector_viewlet.pt')

    def __init__(self, context, request, view, manager=None):
        super(OrgUnitSelectorViewlet, self).__init__(
            context, request, view, manager)

        self.current_unit = None

    def is_available(self):
        return ogds_service().has_multiple_org_units()

    def get_active_unit(self):
        try:
            if not self.current_unit:
                self.current_unit = get_ou_selector().get_current_unit()
        except OperationalError as e:
            logger.exception(e)
        return self.current_unit

    def get_units(self):
        return get_ou_selector().available_units()


class ChangeOrgUnitView(BrowserView):

    def __call__(self):
        unit_id = self.request.get('unit_id')

        if unit_id:
            get_ou_selector().set_current_unit(unit_id)

        return self.request.RESPONSE.redirect(self.context.absolute_url())


class OrgUnitSelectorETagValue(object):
    implements(IETagValue)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        return get_ou_selector().get_current_unit().id()
