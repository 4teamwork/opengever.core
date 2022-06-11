from opengever.ogds.base.utils import get_ou_selector
from zope.publisher.browser import BrowserView


class OrgunitSelectorView(BrowserView):

    def has_available_units(self):
        return get_ou_selector().available_units()
