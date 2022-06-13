from plone.app.layout.viewlets import common as base
from zope.component import getMultiAdapter


HTML_TAG = '<span id="ploneLanguage" data-lang="%s"></span>'


class LanguageExposer(base.ViewletBase):
    """Used to expose the current user langauge as
    a data attribute on HTML element.
    """

    def get_current_user_language(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        current_language = portal_state.language()
        return current_language

    def update(self):
        super(LanguageExposer, self).update()
        self.lang = self.get_current_user_language()

    def render(self):
        return HTML_TAG % (self.lang)
