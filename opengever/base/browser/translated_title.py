from opengever.base import _
from opengever.base.behaviors.translated_title import get_active_languages
from opengever.base.behaviors.translated_title import get_inactive_languages
from opengever.base.behaviors.translated_title import TranslatedTitle
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm


class TranslatedTitleFormMixin(object):

    def get_title_fieldname(self, lang):
        return 'ITranslatedTitle.title_{}'.format(lang)

    def omit_non_active_language_fields(self):
        fields_to_remove = []
        for lang in get_inactive_languages():
            fieldname = self.get_title_fieldname(lang)
            self.fields = self.fields.omit(fieldname)
            fields_to_remove.append(fieldname)

        for group in self.groups:
            for fieldname in fields_to_remove:
                if fieldname in group.fields:
                    group.fields = group.fields.omit(fieldname)

    def adjust_title_on_language_fields(self):
        """If there is only one language specific title field available,
        we ajdust the label to a `Title`.
        """
        supported_languages = set(TranslatedTitle.SUPPORTED_LANGUAGES)
        supported_active_languages = supported_languages.intersection(
            set(get_active_languages()))

        if len(supported_active_languages) == 1:
            fieldname = self.get_title_fieldname(
                list(supported_active_languages)[0])
            if fieldname in self.widgets:
                self.widgets[fieldname].label = _(u"label_title", default=u"Title")

    def adjust_title_on_language_fields_in_groups(self):
        """If there is only one language specific title field available,
        we ajdust the label to a `Title`, also in groups
        """
        supported_languages = set(TranslatedTitle.SUPPORTED_LANGUAGES)
        supported_active_languages = supported_languages.intersection(
            set(get_active_languages()))

        if len(supported_active_languages) == 1:
            fieldname = self.get_title_fieldname(
                list(supported_active_languages)[0])
            for group in self.groups:
                if fieldname in group.widgets:
                    group.widgets[fieldname].label = _(u"label_title",
                                                       default=u"Title")


class TranslatedTitleAddForm(DefaultAddForm, TranslatedTitleFormMixin):

    def updateFields(self):
        super(DefaultAddForm, self).updateFields()
        self.omit_non_active_language_fields()

    def updateWidgets(self):
        super(DefaultAddForm, self).updateWidgets()
        self.adjust_title_on_language_fields()

    def update(self):
        super(TranslatedTitleAddForm, self).update()
        self.adjust_title_on_language_fields_in_groups()


class TranslatedTitleEditForm(DefaultEditForm, TranslatedTitleFormMixin):

    def updateFields(self):
        super(DefaultEditForm, self).updateFields()
        self.omit_non_active_language_fields()

    def updateWidgets(self):
        super(DefaultEditForm, self).updateWidgets()
        self.adjust_title_on_language_fields()

    def update(self):
        super(TranslatedTitleEditForm, self).update()
        self.adjust_title_on_language_fields_in_groups()
