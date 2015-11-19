from opengever.base import _
from plone import api
from plone.directives.dexterity import AddForm
from plone.directives.dexterity import EditForm
from z3c.form.interfaces import HIDDEN_MODE
import martian


TRANSLATED_TITLE_FIELDS = {'de-ch': 'ITranslatedTitle.title_de',
                           'fr-ch': 'ITranslatedTitle.title_fr'}


class TranslatedTitleFormMixin(object):

    def hide_non_active_language_fields(self):
        for lang, fieldname in TRANSLATED_TITLE_FIELDS.items():
            if lang not in self.lang_tool.supported_langs:
                self.widgets[fieldname].mode = HIDDEN_MODE


    def adjust_title_on_language_fields(self):
        """If there is only one language specific title field available,
        we ajdust the label to a `Title`.
        """

        active_languages = [lang for lang in TRANSLATED_TITLE_FIELDS.keys()
                            if lang in self.lang_tool.supported_langs]

        if len(active_languages) == 1:
            fieldname = TRANSLATED_TITLE_FIELDS[active_languages[0]]
            self.widgets[fieldname].label = _(u"label_title", default=u"Title")


class TranslatedTitleAddForm(AddForm, TranslatedTitleFormMixin):

    martian.baseclass()

    def updateWidgets(self):
        super(AddForm, self).updateWidgets()
        self.lang_tool = api.portal.get_tool('portal_languages')
        self.hide_non_active_language_fields()
        self.adjust_title_on_language_fields()


class TranslatedTitleEditForm(EditForm, TranslatedTitleFormMixin):

    martian.baseclass()

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()
        self.lang_tool = api.portal.get_tool('portal_languages')
        self.hide_non_active_language_fields()
        self.adjust_title_on_language_fields()
