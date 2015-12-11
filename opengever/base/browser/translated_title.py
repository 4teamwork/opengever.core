from opengever.base import _
from opengever.base.behaviors.translated_title import TranslatedTitle
from plone import api
from plone.directives.dexterity import AddForm
from plone.directives.dexterity import EditForm
import martian


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
                self.fields = self.fields.omit(self.get_title_fieldname(lang))

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
            self.widgets[fieldname].label = _(u"label_title", default=u"Title")


class TranslatedTitleAddForm(AddForm, TranslatedTitleFormMixin):

    martian.baseclass()

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.omit_non_active_language_fields()

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.adjust_title_on_language_fields()


class TranslatedTitleEditForm(EditForm, TranslatedTitleFormMixin):

    martian.baseclass()

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.omit_non_active_language_fields()

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.adjust_title_on_language_fields()
