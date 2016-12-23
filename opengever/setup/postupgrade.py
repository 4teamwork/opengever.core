from opengever.setup.hooks import reorder_css_resources
from opengever.setup.hooks import reorder_js_resources


class DefaultProfilePostUpgradeAdapter(object):

    def __init__(self, portal, request):
        self.portal = portal
        self.request = request

    def __call__(self):
        reorder_css_resources(self.portal)
        reorder_js_resources(self.portal)
