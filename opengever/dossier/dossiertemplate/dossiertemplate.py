from Acquisition import aq_inner
from Acquisition import aq_parent
from opengever.base.vocabulary import voc_term_title
from opengever.dossier import _
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateMarker
from opengever.dossier.dossiertemplate.behaviors import IDossierTemplateSchema
from opengever.dossier.dossiertemplate.interfaces import IDossierTemplateSettings
from opengever.dossier.interfaces import IDossierContainerTypes
from opengever.dossier.utils import truncate_ellipsis
from opengever.ogds.base.actor import Actor
from plone import api
from plone.dexterity.content import Container
from plone.dexterity.utils import getAdditionalSchemata
from plone.z3cform.fieldsets.utils import remove
from zope.schema import getFieldsInOrder
from plone.dexterity.browser import add
from plone.dexterity.browser import edit


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


class DossierTemplateAddForm(add.DefaultAddForm):

    @property
    def label(self):
        if IDossierTemplateSchema.providedBy(self.context):
            return _(u'Add Subdossier')
        return super(DossierTemplateAddForm, self).label

    def updateFields(self):
        super(DossierTemplateAddForm, self).updateFields()
        whitelist_form_fields(self, TEMPLATABLE_FIELDS)


class DossierTemplateAddView(add.DefaultAddView):
    form = DossierTemplateAddForm


class DossierTemplateEditForm(edit.DefaultEditForm):

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
                key = '{}.{}'.format(schema.__name__, fieldname)
                if key not in TEMPLATABLE_FIELDS:
                    continue

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
        return voc_term_title(IDossier['filing_prefix'],
                              IDossier(self).filing_prefix)

    def get_responsible_actor(self):
        return Actor.user(IDossier(self).responsible)

    @property
    def responsible_label(self):
        return self.get_responsible_actor().get_label()

    def get_formatted_comments(self, threshold=400):
        """Returns the dossier's comment truncated to characters defined
        in `threshold` and transformed as web intelligent text.
        """
        comments = IDossier(self).comments
        if comments:
            if threshold:
                comments = truncate_ellipsis(comments, threshold)
            return api.portal.get_tool(name='portal_transforms').convertTo(
                'text/html', comments, mimetype='text/x-web-intelligent').getData()
