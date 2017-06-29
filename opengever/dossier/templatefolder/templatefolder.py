from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.templatefolder import ITemplateFolder
from plone.dexterity.content import Container
from Acquisition import aq_parent
from Acquisition import aq_inner


class TemplateFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.dossier.templatefolder')


class TemplateFolderEditForm(TranslatedTitleEditForm):
    grok.context(ITemplateFolder)


class TemplateFolder(Container, TranslatedTitleMixin):
    """Base class for template folder."""

    Title = TranslatedTitleMixin.Title

    def is_subtemplatefolder(self):
        parent = aq_parent(aq_inner(self))
        return bool(ITemplateFolder.providedBy(parent))
