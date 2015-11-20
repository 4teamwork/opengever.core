from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.base import DossierContainer
from opengever.dossier.templatedossier import ITemplateDossier


class TemplateDossierAddForm(TranslatedTitleAddForm):
    grok.name('opengever.dossier.templatedossier')


class TemplateDossierEditForm(TranslatedTitleEditForm):
    grok.context(ITemplateDossier)


class TemplateDossier(DossierContainer, TranslatedTitleMixin):
    """Base class for template dossiers."""


    Title = TranslatedTitleMixin.Title
