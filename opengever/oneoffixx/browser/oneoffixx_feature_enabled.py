from opengever.oneoffixx import is_oneoffixx_feature_enabled
from Products.Five import BrowserView


class OneoffixxFeatureEnabledView(BrowserView):

    def __call__(self):
        return is_oneoffixx_feature_enabled()
