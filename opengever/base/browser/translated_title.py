from opengever.base import _
from opengever.base.behaviors.translated_title import TranslatedTitle
from opengever.base.formutils import omit_field_by_name
from opengever.base.formutils import widget_by_name
from plone import api
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm


class TranslatedTitleFormMixin(object):

    def get_active_languages(self):
        """Returns a list of the current languages
        """
        lang_tool = api.portal.get_tool('portal_languages')
        return [lang.split('-')[0] for lang in lang_tool.supported_langs]

    def get_title_fieldname(self, lang):
        return 'ITranslatedTitle.title_{}'.format(lang)

    def omit_non_active_language_fields(self):
        for lang in TranslatedTitle.SUPPORTED_LANGUAGES:
            if lang not in self.get_active_languages():
                fieldname = self.get_title_fieldname(lang)
                omit_field_by_name(self, fieldname)

    def adjust_title_on_language_fields(self):
        """If there is only one language specific title field available,
        we ajdust the label to a `Title`.
        """
        supported_languages = set(TranslatedTitle.SUPPORTED_LANGUAGES)
        supported_active_languages = supported_languages.intersection(
            set(self.get_active_languages()))

        if len(supported_active_languages) == 1:
            fieldname = self.get_title_fieldname(
                list(supported_active_languages)[0])
            widget = widget_by_name(self, fieldname)
            if widget:
                widget.label = _(u"label_title", default=u"Title")


class TranslatedTitleAddForm(DefaultAddForm, TranslatedTitleFormMixin):

    # XXX cooperative multiple inheritance seems to be broken for the TTFM

    def updateFields(self):
        super(TranslatedTitleAddForm, self).updateFields()
        self.omit_non_active_language_fields()

    def update(self):
        super(TranslatedTitleAddForm, self).update()
        self.adjust_title_on_language_fields()


class TranslatedTitleEditForm(DefaultEditForm, TranslatedTitleFormMixin):

    def updateFields(self):
        super(TranslatedTitleEditForm, self).updateFields()
        self.omit_non_active_language_fields()

    def update(self):
        super(TranslatedTitleEditForm, self).update()
        self.adjust_title_on_language_fields()
