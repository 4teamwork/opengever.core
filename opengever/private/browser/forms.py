from five import grok
from opengever.dossier.behaviors.dossier import AddForm


class PrivateDossierAddForm(AddForm):
    grok.name('opengever.private.dossier')
