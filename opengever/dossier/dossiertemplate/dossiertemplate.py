from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.vocabulary import voc_term_title
from opengever.dossier import _
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplate
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.utils import truncate_ellipsis
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


class DossierTemplateAddView(add.DefaultAddView):
    form = DossierTemplateAddForm


class DossierTemplateEditForm(edit.DefaultEditForm):

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(aq_parent(aq_inner(self.context))):
            return _(u'Edit Subdossier')
        return super(DossierTemplateEditForm, self).label


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
                        **kwargs):

        subdossiers = api.content.find(self, object_provides=IDossierTemplateMarker,
                                       sort_order=sort_order, sort_on=sort_on)

        # Remove the object itself from the list of subdossiers
        current_uid = self.UID()
        subdossiers = [s for s in subdossiers
                       if not s.UID == current_uid]

        return subdossiers

    def get_filing_prefix_label(self):
        return voc_term_title(IDossierTemplate['filing_prefix'],
                              IDossierTemplate(self).filing_prefix)

    def get_formatted_comments(self, threshold=400):
        """Returns the dossier's comment truncated to characters defined
        in `threshold` and transformed as web intelligent text.
        """
        comments = IDossierTemplate(self).comments
        if comments:
            if threshold:
                comments = truncate_ellipsis(comments, threshold)
            return api.portal.get_tool(name='portal_transforms').convertTo(
                'text/html', comments, mimetype='text/x-web-intelligent').getData()
