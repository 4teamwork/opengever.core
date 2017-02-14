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
    """XXX Legacy class from rename TemplateFolder to TemplateDossier.

    Leave this class until each GEVER-installation is updated to the version
    containing this changes.
    """
