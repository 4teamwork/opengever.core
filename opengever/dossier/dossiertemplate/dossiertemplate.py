from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.behaviors.utils import hide_fields_from_behavior
from opengever.base.vocabulary import voc_term_title
from opengever.dossier import _
from opengever.dossier import is_dossier_checklist_feature_enabled
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from plone import api
from plone.dexterity.browser import add
from plone.dexterity.browser import edit
from plone.dexterity.content import Container
from plone.dexterity.utils import getAdditionalSchemata
from zope.schema import getFieldsInOrder


BEHAVIOR_INTERFACE_MAPPING = {
    'IDossier': 'IDossierTemplate'
}


class DossierTemplateAddForm(add.DefaultAddForm):

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(self.context):
            return _(u'Add Subdossier')
        return super(DossierTemplateAddForm, self).label

    def updateFields(self):
        super(DossierTemplateAddForm, self).updateFields()
        fields = []
        if not is_dossier_checklist_feature_enabled():
            fields.append('IDossierTemplate.checklist')

        hide_fields_from_behavior(self, fields)


class DossierTemplateAddView(add.DefaultAddView):
    form = DossierTemplateAddForm


class DossierTemplateEditForm(edit.DefaultEditForm):

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        return super(DossierTemplateEditForm, self).label

    def updateFields(self):
        super(DossierTemplateEditForm, self).updateFields()
        fields = []
        if not is_dossier_checklist_feature_enabled():
            fields.append('IDossierTemplate.checklist')

        hide_fields_from_behavior(self, fields)


class DossierTemplate(Container):
    """Base class for template dossiers."""

    def allowedContentTypes(self, *args, **kwargs):
        types = super(
            DossierTemplate, self).allowedContentTypes(*args, **kwargs)

        if not self.is_subdossier_allowed():
            types = filter(
                lambda x: x.id != 'opengever.dossier.dossiertemplate', types)

        return types

    def is_subdossier_allowed(self):
        if self.is_respect_max_dossier_depth:
            max_dossier_depth = api.portal.get_registry_record(
                'maximum_dossier_depth', interface=IDossierContainerTypes)

            current_levels = len([item for item in self.aq_chain
                                  if IDossierTemplateSchema.providedBy(item)])
            return current_levels <= max_dossier_depth

        return True

    @property
    def is_respect_max_dossier_depth(self):
        return api.portal.get_registry_record(
            'respect_max_depth', interface=IDossierTemplateSettings)

    def is_subdossier(self):
        parent = aq_parent(aq_inner(self))
        return bool(IDossierTemplateSchema.providedBy(parent))

    def get_schema_values(self):
        values = {}
        for schema in getAdditionalSchemata(self):
            for fieldname, field in getFieldsInOrder(schema):
                # Readonly fields are not templatable (e.g. changed)
                if field.readonly:
                    continue
                key = '{}.{}'.format(schema.__name__, fieldname)
                values[key] = getattr(field.interface(self), fieldname)
        return values

    def is_subdossier_addable(self):
        """We do not restrict dossier depth in a dossiertemplate.
        """
        return True

    def get_main_dossier(self):
        dossier = self
        while dossier.is_subdossier():
            dossier = aq_parent(aq_inner(dossier))

        return dossier

    def has_subdossiers(self):
        return len(self.get_subdossiers()) > 0

    def get_subdossiers(self, sort_on='sortable_title',
                        sort_order='ascending',
                        unrestricted=False,
                        **kwargs):

        dossier_path = '/'.join(self.getPhysicalPath())
        query = {
            'path': dict(query=dossier_path),
            'object_provides': IDossierTemplateMarker.__identifier__,
            'sort_on': sort_on,
            'sort_order': sort_order
        }

        if unrestricted:
            subdossiers = self.portal_catalog.unrestrictedSearchResults(query)
        else:
            subdossiers = self.portal_catalog(query)

        # Remove the object itself from the list of subdossiers
        current_uid = self.UID()
        subdossiers = [s for s in subdossiers
                       if not s.UID == current_uid]

        return subdossiers

    def is_dossier_structure_addable(self, additional_depth=1):
        """Checks if the maximum dossier depth allows additional_depth levels
        of subdossiers
        """
        max_depth = api.portal.get_registry_record(
            name='maximum_dossier_depth',
            interface=IDossierContainerTypes,
            default=100,
        )

        depth = 0
        obj = self
        while IDossierTemplateMarker.providedBy(obj):
            depth += 1
            obj = aq_parent(aq_inner(obj))

        return depth + additional_depth <= max_depth + 1

    def get_filing_prefix_label(self):
        return voc_term_title(IDossierTemplate['filing_prefix'],
                              IDossierTemplate(self).filing_prefix)
