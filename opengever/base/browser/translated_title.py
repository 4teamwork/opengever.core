from opengever.base import _
from plone import api
from plone.directives.dexterity import AddForm
from plone.directives.dexterity import EditForm
import martian


TRANSLATED_TITLE_FIELDS = {'de-ch': 'ITranslatedTitle.title_de',
                           'fr-ch': 'ITranslatedTitle.title_fr'}


class TranslatedTitleFormMixin(object):

    def omit_non_active_language_fields(self):
        lang_tool = api.portal.get_tool('portal_languages')
        for lang, fieldname in TRANSLATED_TITLE_FIELDS.items():
            if lang not in lang_tool.supported_langs:
                self.fields = self.fields.omit(fieldname)

    def adjust_title_on_language_fields(self):
        """If there is only one language specific title field available,
        we ajdust the label to a `Title`.
        """
        lang_tool = api.portal.get_tool('portal_languages')
        active_languages = [lang for lang in TRANSLATED_TITLE_FIELDS.keys()
                            if lang in lang_tool.supported_langs]

        if len(active_languages) == 1:
            fieldname = TRANSLATED_TITLE_FIELDS[active_languages[0]]
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
