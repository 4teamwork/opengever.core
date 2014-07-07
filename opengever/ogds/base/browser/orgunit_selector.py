from zope.publisher.browser import BrowserView
from opengever.ogds.base.utils import get_ou_selector

class OrgunitSelectorView(BrowserView):

    def has_available_units(self):
        return get_ou_selector().available_units()
        