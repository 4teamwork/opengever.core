from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.dossier.base import DossierContainer


class TemplateDossier(DossierContainer, TranslatedTitleMixin):
    """Base class for template dossiers."""

    Title = TranslatedTitleMixin.Title
