from opengever.base.interfaces import ISQLObjectWrapper
from opengever.bumblebee import is_bumblebee_feature_enabled
from opengever.meeting import is_meeting_feature_enabled
from plone.app.layout.globals.layout import LayoutPolicy
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility


class GeverLayoutPolicy(LayoutPolicy):
    """Adds gever specific layout configurations
    """

    def bodyClass(self, template, view):
        """Extends the default body class with the `feature-bumblebee` class, if
        the bumblebeefeature is enabled.
        """
        classes = [super(GeverLayoutPolicy, self).bodyClass(template, view)]

        if is_bumblebee_feature_enabled():
            classes.append('feature-bumblebee')

        if is_meeting_feature_enabled():
            classes.append('feature-word-meeting')

        if ISQLObjectWrapper.providedBy(self.context):
            normalize = getUtility(IIDNormalizer).normalize
            classes.append('model-{}'.format(
                normalize(type(self.context.model).__name__)))

        return ' '.join(classes)
