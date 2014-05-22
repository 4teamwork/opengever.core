from ooxml_docprops import is_supported_mimetype
from ooxml_docprops import update_properties
from opengever.dossier.interfaces import IDocProperties
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from tempfile import NamedTemporaryFile
from z3c.form.interfaces import IValue
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder
import os


NO_DEFAULT_VALUE_FIELDS = ['title', 'file']


class TemporaryDocFile(object):

    def __init__(self, file_):
        self.file = file_
        self.path = None

    def __enter__(self):
        template_data = self.file.data

        with NamedTemporaryFile(delete=False) as tmpfile:
            self.path = tmpfile.name
            tmpfile.write(template_data)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.path)


class DocumentFromTemplate(object):
    """Create a new document from templates.

    """
    def __init__(self, template_doc):
        self.template_doc = template_doc
        self.file = template_doc.file

    def create_in(self, context, title, with_properties=False):
        if (with_properties and
                is_supported_mimetype(self.template_doc.file.contentType)):
            data = self._copy_doc_properties_from_template(context)
        else:
            data = self.file.data

        _type = self._get_primary_field_type(self.template_doc)
        new_file = _type(data=data, filename=self.file.filename)

        new_doc = createContentInContainer(
            context, 'opengever.document.document',
            title=title, file=new_file)

        self._set_defaults(new_doc)

        # Notify necessary standard event handlers
        notify(ObjectModifiedEvent(new_doc))
        return new_doc

    def _copy_doc_properties_from_template(self, dossier):
        # Copy the file data of the template to a temporary file

        with TemporaryDocFile(self.template_doc.file) as tmpfile:

            # Get properties for the new document based on the dossier
            properties_adapter = getMultiAdapter(
                (dossier, dossier.REQUEST), IDocProperties)
            properties = properties_adapter.get_properties()

            # Set the DocProperties by modifying the temporary file
            update_properties(tmpfile.path, properties)

            # Create a new NamedBlobFile from the updated temporary file's data
            with open(tmpfile.path) as processed_tmpfile:
                populated_template_data = processed_tmpfile.read()

        return populated_template_data

    def _get_primary_field_type(self, obj):
        """Determine the type of an objects primary field (e.g. NamedBlobFile)
        so we can use it as a factory when setting the new document's primary
        field.
        """

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if IPrimaryField.providedBy(field):
                    return field._type

    def _set_defaults(self, obj):
        """Set default values for all fields including behavior fields."""

        for schemata in iterSchemata(obj):
            for name, field in getFieldsInOrder(schemata):
                if name not in NO_DEFAULT_VALUE_FIELDS:
                    default = queryMultiAdapter(
                        (obj, obj.REQUEST, None, field, None),
                        IValue, name='default')

                    if default is not None:
                        default = default.get()
                    if default is None:
                        default = getattr(field, 'default', None)
                    if default is None:
                        try:
                            default = field.missing_value
                        except AttributeError:
                            pass
                    value = default
                    field.set(field.interface(obj), value)
