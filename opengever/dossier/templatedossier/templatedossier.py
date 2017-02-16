from opengever.base.behaviors.translated_title import TranslatedTitleMixin
from opengever.dossier.base import DossierContainer


class TemplateDossier(DossierContainer, TranslatedTitleMixin):
    """XXX Legacy class from rename TemplateFolder to TemplateDossier.

    Leave this class until each GEVER-installation is updated to the version
    containing this changes.
    """
