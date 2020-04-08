from opengever.base.command import BaseObjectCreatorCommand
from opengever.base.command import CreateDocumentCommand
from opengever.base.role_assignments import RoleAssignment
from opengever.base.role_assignments import RoleAssignmentManager
from opengever.document.docprops import DocPropertyWriter
from opengever.document.handlers import DISABLE_DOCPROPERTY_UPDATE_FLAG
from opengever.dossier.dossiertemplate.dossiertemplate import BEHAVIOR_INTERFACE_MAPPING
from plone.dexterity.utils import iterSchemataForType
from zope.globalrequest import getRequest


class CreateDocumentFromTemplateCommand(CreateDocumentCommand):
    """Store a copy of the template in the new document's primary file field
    """

    def __init__(self, context, template_doc, title, recipient_data=tuple()):
        data = getattr(template_doc.get_file(), "data", None)
        super(CreateDocumentFromTemplateCommand, self).__init__(
            context, template_doc.get_filename(), data,
            title=title)
        self.recipient_data = recipient_data

        # Grab blocking of role inheritance
        self.block_role_inheritance = getattr(
            template_doc, '__ac_local_roles_block__', None)

        # Grab the local roles assignations from the template, if any
        self.role_assignments = None
        manager = RoleAssignmentManager(template_doc)
        if manager.has_storage():
            self.role_assignments = tuple(
                RoleAssignment(**assignment)
                for assignment in manager.storage.get_all()
            )

    def execute(self):
        # The blob will be overwritten just afterwards when we add
        # the recepient data to the docproperties. Solr will then
        # be unable to process that blob.
        getRequest().set(DISABLE_DOCPROPERTY_UPDATE_FLAG, True)
        obj = super(CreateDocumentFromTemplateCommand, self).execute()

        getRequest().set(DISABLE_DOCPROPERTY_UPDATE_FLAG, False)
        DocPropertyWriter(obj, recipient_data=self.recipient_data).initialize()

        # Set blocking of role inheritance based on the template object
        if self.block_role_inheritance is not None:
            obj.__ac_local_roles_block__ = self.block_role_inheritance

        # Copy the local roles assignations over from the template
        if self.role_assignments is not None:
            manager = RoleAssignmentManager(obj)
            # Passing an empty iterable in here creates an empty mapping
            manager.add_or_update_assignments(self.role_assignments)
        return obj


class CreateDossierFromTemplateCommand(BaseObjectCreatorCommand):
    """Creates a new dossier based on the dossiertemplate.
    """
    portal_type = 'opengever.dossier.businesscasedossier'

    def __init__(self, context, template):
        kw = self._get_additional_attributes(template)
        self.fields = kw["IOpenGeverBase"]
        del kw["IOpenGeverBase"]
        self.additional_fields = kw

        # Grab blocking of role inheritance
        self.block_role_inheritance = getattr(
            template, '__ac_local_roles_block__', None)

        # Grab the local roles assignations from the template, if any
        self.role_assignments = None
        manager = RoleAssignmentManager(template)
        if manager.has_storage():
            self.role_assignments = tuple(
                RoleAssignment(**assignment)
                for assignment in manager.storage.get_all()
            )

        super(CreateDossierFromTemplateCommand, self).__init__(
            context, **self.fields)

    def execute(self):
        obj = super(CreateDossierFromTemplateCommand, self).execute()
        schemas = iterSchemataForType(self.portal_type)
        for schema in schemas:
            schema_name = BEHAVIOR_INTERFACE_MAPPING.get(
                schema.getName(), schema.getName())
            if schema_name not in self.additional_fields:
                continue
            behavior = schema(obj)
            for prop_name in self.additional_fields[schema_name]:
                setattr(behavior, prop_name,
                        self.additional_fields[schema_name][prop_name])

        # Set blocking of role inheritance based on the template object
        if self.block_role_inheritance is not None:
            obj.__ac_local_roles_block__ = self.block_role_inheritance

        # Copy the local roles assignations over from the template
        if self.role_assignments is not None:
            manager = RoleAssignmentManager(obj)
            # Passing an empty iterable in here creates an empty mapping
            manager.add_or_update_assignments(self.role_assignments)

        return obj

    def _get_additional_attributes(self, template):
        """Get all templatable attributes defined in the template.
        """
        kw = template.get_schema_values()
        fields = {}
        for key, value in kw.items():
            schema_name, prop_name = key.split(".")
            if schema_name not in fields:
                fields[schema_name] = {}
            fields[schema_name][prop_name] = value
        return fields
