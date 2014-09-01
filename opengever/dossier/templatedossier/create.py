from opengever.dossier.docprops import DocPropertyWriter
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from z3c.form.interfaces import IValue
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema import getFieldsInOrder


NO_DEFAULT_VALUE_FIELDS = ['title', 'file']


class DocumentFromTemplate(object):
    """Create a new document from templates.

    """
    def __init__(self, template_doc):
        self.template_doc = template_doc
        self.file = template_doc.file

    def create_in(self, context, title, with_properties=False):
        data = self.file.data

        _type = self._get_primary_field_type(self.template_doc)
        new_file = _type(data=data, filename=self.file.filename)

        new_doc = createContentInContainer(
            context, 'opengever.document.document',
            title=title, file=new_file)

        self._set_defaults(new_doc)

        DocPropertyWriter.create_properties(new_doc)

        # Notify necessary standard event handlers
        notify(ObjectModifiedEvent(new_doc))
        return new_doc

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
