from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.dossier.base import DossierContainer


class TemplateFolder(DossierContainer, TranslatedTitleMixin):
    """Base class for template folder."""

    Title = TranslatedTitleMixin.Title
