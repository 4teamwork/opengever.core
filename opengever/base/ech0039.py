from Products.CMFPlone.utils import safe_unicode
from ftw.ech0039.bind import BIND
from ftw.ech0039.exportable import FileAdapter
from ftw.ech0039.interfaces import IECH0039Document
from ftw.ech0039.transform import as_token, as_date
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import iterSchemata
from plone.rfc822.interfaces import IPrimaryField
from zope.component import adapts
from zope.interface import implements
from zope.schema import getFieldsInOrder
import os


ECH0039_MAPPING = {
    'keywords': 'keywords',
    'document_date': 'openingDate',
}


class OpengeverDocumentAdapter(FileAdapter):
    implements(IECH0039Document)
    adapts(IDexterityItem)

    def _get_primary_file(self):
        for schemata in iterSchemata(self.context):
            for name, field in getFieldsInOrder(schemata):
                if IPrimaryField.providedBy(field):
                    return field.get(self.context)

    def add_to(self, marshaller):
        if self._get_primary_file():
            marshaller.add_document(self)

    @property
    def file_path(self):
        filename = self._get_primary_file().filename
        _base, file_extension = os.path.splitext(filename)
        return u'files/{}{}'.format(self.uuid, file_extension)

    @property
    def file_content(self):
        return self._get_primary_file().data

    def get_data(self):
        data = super(OpengeverDocumentAdapter, self).get_data()

        for schemata in iterSchemata(self.context):
            for name, field in getFieldsInOrder(schemata):
                if name in ECH0039_MAPPING:
                    value = field.get(self.context)
                    if value:
                        data[ECH0039_MAPPING.get(name)] = value

        keywords = data.get('keywords')
        if keywords:
            keywords = [as_token(safe_unicode(keyword))
                        for keyword in keywords]
            data['keywords'] = BIND(*keywords)

        if data.get('openingDate'):
            data['openingDate'] = as_date(data.get('openingDate'))

        return data
