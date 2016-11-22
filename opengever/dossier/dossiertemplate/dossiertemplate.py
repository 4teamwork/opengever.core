from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.dossier import _
from opengever.dossier.dossiertemplate import IDossierTemplate
from plone.dexterity.content import Container
from plone.directives import dexterity


class DossierTemplateAddForm(dexterity.AddForm):
    grok.name('opengever.dossier.dossiertemplate')

    @property
    def label(self):
        if IDossierTemplate.providedBy(self.context):
            return _(u'Add Subdossier')
        return super(DossierTemplateAddForm, self).label


class DossierTemplateEditForm(dexterity.EditForm):
    grok.context(IDossierTemplate)

    @property
    def label(self):
        if IDossierTemplate.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        return super(DossierTemplateEditForm, self).label


class DossierTemplate(Container):
    """Base class for template dossiers."""

    def is_subdossier(self):
        parent = aq_parent(aq_inner(self))
        return bool(IDossierTemplate.providedBy(parent))
