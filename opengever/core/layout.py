from opengever.bumblebee import is_bumblebee_feature_enabled
from plone.app.layout.globals.layout import LayoutPolicy


class GeverLayoutPolicy(LayoutPolicy):
    """Adds gever specific layout configurations
    """

    def bodyClass(self, template, view):
        """Extends the default body class with the `feature-bumblebee` class, if
        the bumblebeefeature is enabled.
        """
        body_class = super(GeverLayoutPolicy, self).bodyClass(template, view)

        if is_bumblebee_feature_enabled():
            body_class = ' '.join((body_class, 'feature-bumblebee'))

        return body_class
