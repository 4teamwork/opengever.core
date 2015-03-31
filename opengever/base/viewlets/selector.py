from plone.app.i18n.locales.browser.selector import LanguageSelector


class LanguageSelectorMenu(LanguageSelector):
    """Opengever custom language selector, which display the
    selector as a dropdown menu.
    """

    def get_current_language(self):
        for language in self.languages():
            if language.get('selected'):
                return language
