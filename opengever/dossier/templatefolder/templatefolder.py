from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.base import DossierContainer
from opengever.dossier.templatefolder import ITemplateFolder


class TemplateFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.dossier.templatefolder')


class TemplateFolderEditForm(TranslatedTitleEditForm):
    grok.context(ITemplateFolder)


class TemplateFolder(DossierContainer, TranslatedTitleMixin):
    """Base class for template folder."""

    Title = TranslatedTitleMixin.Title
