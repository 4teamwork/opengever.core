from AccessControl import Unauthorized
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

    def renderBase(self):
        """Fixes the base url in the case of contentish objects.
        LayoutPolicy incorrectly returns the request URL for contentish
        objects, including the view name.
        This is fixed in Plone 4.3.16 by introducing a new data attribute
        on the body tag, data-base-url, which should contain the correct
        base url, but actually also has a bug in a fallback setting the
        url to the referer.
        Moreover we make sure that the base url ends with a slash as
        the browser will cut it to the last slash
        """
        context = self.context

        # when accessing via WEBDAV you're not allowed to access aq_base
        try:
            return context.absolute_url().rstrip('/') + '/'
        except Unauthorized:
            pass
