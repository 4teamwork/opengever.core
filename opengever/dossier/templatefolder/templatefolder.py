from AccessControl import getSecurityManager
from five import grok
from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.base.browser.translated_title import TranslatedTitleAddForm
from opengever.base.browser.translated_title import TranslatedTitleEditForm
from opengever.dossier.base import DossierContainer
from opengever.dossier.templatefolder import ITemplateFolder


class TemplateFolderAddForm(TranslatedTitleAddForm):
    grok.name('opengever.dossier.templatefolder')

    def update(self):
        """Adds a default value for `responsible` to the request so the
        field is prefilled with the current user, or the parent dossier's
        responsible in the case of a subdossier.
        """
        responsible = getSecurityManager().getUser().getId()

        if not self.request.get('form.widgets.IDossier.responsible', None):
            self.request.set('form.widgets.IDossier.responsible',
                             [responsible])
        super(TemplateFolderAddForm, self).update()


class TemplateFolderEditForm(TranslatedTitleEditForm):
    grok.context(ITemplateFolder)


class TemplateFolder(DossierContainer, TranslatedTitleMixin):
    """Base class for template folder."""

    Title = TranslatedTitleMixin.Title
