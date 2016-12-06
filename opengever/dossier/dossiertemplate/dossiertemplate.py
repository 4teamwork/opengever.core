from Acquisition import aq_inner
from Acquisition import aq_parent
from five import grok
from opengever.dossier import _
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from plone.dexterity.content import Container
from plone.dexterity.utils import getAdditionalSchemata
from plone.directives import dexterity
from plone.z3cform.fieldsets.utils import remove
from zope.schema import getFieldsInOrder

TEMPLATABLE_FIELDS = [
    'IOpenGeverBase.title',
    'IOpenGeverBase.description',
    'IDossierTemplate.keywords',
    'IDossierTemplate.comments',
    'IDossierTemplate.filing_prefix',
    ]

BEHAVIOR_INTERFACE_MAPPING = {
    'IDossier': 'IDossierTemplate'
    }


def whitelist_form_fields(form, whitlisted_fields):
    """Removes all fields instead the whitelisted fields from the form.
    """
    for schema in getAdditionalSchemata(form):
        behavior_interface_name = schema.__name__
        for fieldname in schema:
            full_name = '{}.{}'.format(behavior_interface_name, fieldname)
            if full_name in whitlisted_fields:
                continue

            remove(form, fieldname, behavior_interface_name)


class DossierTemplateAddForm(dexterity.AddForm):
    grok.name('opengever.dossier.dossiertemplate')

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(self.context):
            return _(u'Add Subdossier')
        return super(DossierTemplateAddForm, self).label

    def updateFields(self):
        super(DossierTemplateAddForm, self).updateFields()
        whitelist_form_fields(self, TEMPLATABLE_FIELDS)


class DossierTemplateEditForm(dexterity.EditForm):
    grok.context(IDossierTemplateSchema)

    def updateFields(self):
        super(DossierTemplateEditForm, self).updateFields()
        whitelist_form_fields(self, TEMPLATABLE_FIELDS)

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        return super(DossierTemplateEditForm, self).label


class DossierTemplate(Container):
    """Base class for template dossiers."""

    def is_subdossier(self):
        parent = aq_parent(aq_inner(self))
        return bool(IDossierTemplateSchema.providedBy(parent))

    def get_schema_values(self):
        values = {}
        for schema in getAdditionalSchemata(self):
            for fieldname, field in getFieldsInOrder(schema):
                key = '{}.{}'.format(schema.__name__, fieldname)
                if key not in TEMPLATABLE_FIELDS:
                    continue

                values[key] = getattr(field.interface(self), fieldname)
        return values
