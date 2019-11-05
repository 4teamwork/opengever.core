from datetime import datetime
from docx import Document
from docxcompose.properties import CustomProperties
from docxcompose.sdt import StructuredDocumentTags
from opengever import journal
from opengever.base.date_time import ulocalized_time
from opengever.dossier.interfaces import IDocProperties
from opengever.dossier.interfaces import ITemplateFolderProperties
from opengever.meeting.interfaces import IMeetingSettings
from plone import api
from plone.registry.interfaces import IRegistry
from tempfile import NamedTemporaryFile
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
import os


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


class DocPropertyWriter(object):
    """Write doc-properties for a document.

    The optional argument recipient_data is an iterable of doc-property
    providers that are added to the document with a "recipient" prefix.
    """

    def __init__(self, document, recipient_data=tuple()):
        self.recipient_data = recipient_data
        self.document = document
        self.request = self.document.REQUEST
        self.date_format = api.portal.get_registry_record(
            "sablon_date_format_string", interface=IMeetingSettings)

    def update(self):
        if self.update_doc_properties(only_existing=True):
            journal.handlers.doc_properties_updated(self.document)

    def initialize(self):
        self.update_doc_properties(only_existing=False)

    def get_properties(self):
        properties_adapter = getMultiAdapter(
            (self.document, self.request), IDocProperties)
        return properties_adapter.get_properties(self.recipient_data)

    def is_export_enabled(self):
        registry = getUtility(IRegistry)
        props = registry.forInterface(ITemplateFolderProperties)
        return props.create_doc_properties

    def update_doc_properties(self, only_existing):
        if not self.is_export_enabled():
            return False
        if not self.has_file():
            return False
        if not self.is_supported_file():
            return False

        return self.write_properties(only_existing, self.get_properties())

    def write_properties(self, only_existing, properties):
        with TemporaryDocFile(self.document.file) as tmpfile:
            changed = False

            doc = Document(tmpfile.path)

            props = CustomProperties(doc)

            if not only_existing or any(key in props for key in properties.keys()):
                for key, value in properties.items():
                    # Docproperties must have a value.
                    # In case of None we delete the property an set it's cached
                    # value to empty string. We keep the field in the document
                    # as the property may get a value in a later update.
                    if value is None:
                        if key in props:
                            del props[key]
                        props.update(key, u'')
                    else:
                        props[key] = value
                    changed = True

            if changed:
                # Update cached properties
                CustomProperties(doc).update_all()

            # Update content controls
            sdts = StructuredDocumentTags(doc)
            for key, value in properties.items():
                tags = sdts.tags_by_alias(key)
                if tags:
                    if isinstance(value, str):
                        value = value.decode('utf8')
                    elif isinstance(value, (int, float)):
                        value = unicode(value)
                    elif isinstance(value, datetime):
                        value = ulocalized_time(
                            value, self.date_format, self.request)
                    elif value is None:
                        value = u''
                    sdts.set_text(key, value)
                    changed = True

            if changed:
                doc.save(tmpfile.path)

                with open(tmpfile.path) as processed_tmpfile:
                    file_data = processed_tmpfile.read()

                self.document.update_file(file_data)
                notify(ObjectModifiedEvent(self.document))

            return changed

    def has_file(self):
        return self.document.file is not None

    def is_supported_file(self):
        return self.document.file.contentType in [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        ]
