from opengever.activity import notification_center
from plone import api
from zope.i18n import translate


class BaseActivity(object):
    """Abstract base class for all activities.

    The BaseActivity class is a representation for every activity which can
    be performed on an object. It provides every needed attribute/methods to
    record the activity in the notification center.

    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.center = notification_center()

    @property
    def kind(self):
        raise NotImplementedError()

    @property
    def title(self):
        return self.translate_to_all_languages(self.context.title)

    @property
    def actor_id(self):
        return api.user.get_current().getId()

    @property
    def summary(self):
        raise NotImplementedError()

    @property
    def description(self):
        raise NotImplementedError()

    def before_recording(self):
        """Will be called before adding the activity to the
        notification center (see method `record`). Used for watcher
        adjustments ect.
        """
        pass

    def after_recording(self):
        """Will be called after adding the activity to the
        notification center (see method `record`). Used for watcher
        adjustments ect.
        """
        pass

    def record(self):
        """Adds the activity itself to the notification center.
        """
        self.before_recording()

        self.center.add_activity(
            self.context,
            self.kind,
            self.title,
            self.label,
            self.summary,
            self.actor_id,
            self.description)

        self.after_recording()

    def translate_to_all_languages(self, msg):
        values = {}
        for code in self._get_supported_languages():
            values[code] = translate(msg, context=self.request, target_language=code)

        return values

    def translate(self, msg, language):
        return translate(msg, context=self.request, target_language=language)

    def _get_supported_languages(self):
        """Returns a list of codes of all supported language.
        """
        lang_tool = api.portal.get_tool('portal_languages')
        return [code.split('-')[0] for code in lang_tool.getSupportedLanguages()]
