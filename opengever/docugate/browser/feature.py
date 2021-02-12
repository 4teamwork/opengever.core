from opengever.docugate import is_docugate_feature_enabled
from Products.Five import BrowserView


class DocugateFeatureEnabledView(BrowserView):

    def __call__(self):
        return is_docugate_feature_enabled()
