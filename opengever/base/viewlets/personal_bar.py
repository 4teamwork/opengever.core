from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.layout.viewlets import common
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PersonalBarViewlet(common.PersonalBarViewlet):
    """Personal bar viewlet showing the user portrait image.
    """
    index = ViewPageTemplateFile('personal_bar.pt')

    def update(self):
        super(PersonalBarViewlet, self).update()
        self._update_user_actions_with_languages(self.user_actions)

    def _update_user_actions_with_languages(self, actions):
        language_selector = LanguageSelector(self.context,
                                             self.request,
                                             self.view,
                                             self.manager)
        language_selector.update()
        langs = language_selector.languages()
        langs.reverse()

        if len(langs) == 1:
            return

        for index, lang in enumerate(langs):
            switch_lang_url = '{0}/switchLanguage?set_language={1}'.format(
                self.context.absolute_url(), lang['code'])

            actions.insert(0, {'category': 'language',
                               'descrption': '',
                               'title': lang['native'],
                               'url': switch_lang_url,
                               'code': lang['code'],
                               'selected': lang['selected'],
                               'id': 'lang-{0}'.format(lang['code']),
                               'separator': index == 0
                               })

    def portrait_url(self):
        mtool = getToolByName(self.context, 'portal_membership')
        portrait = mtool.getPersonalPortrait()
        if portrait is not None:
            return portrait.absolute_url()
        utool = getToolByName(self.context, 'portal_url')
        return '%s/defaultUser.png' % utool()
