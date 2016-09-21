from opengever.officeatwork import is_officeatwork_feature_enabled
from Products.Five import BrowserView


class OfficeatworkFeatureEnabledView(BrowserView):

    def __call__(self):
        return is_officeatwork_feature_enabled()
