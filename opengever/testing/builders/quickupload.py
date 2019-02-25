from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import builder_registry
from ftw.builder.builder import PloneObjectBuilder
from opengever.testing import assets
from zope.component import getAdapter
import mimetypes
import os


class QuickuploadMailBuilder(PloneObjectBuilder):

    def __init__(self, session):
        super(QuickuploadMailBuilder, self).__init__(session)
        self.data = None
        self.filename = 'mail.eml'

    def create_object(self, **kwargs):
        factory = getAdapter(self.container, IQuickUploadFileFactory)
        assert factory, 'invalid container'

        result = factory(filename=self.filename,
                         title='',  # ignored by adapter
                         description=None,
                         content_type='message/rfc822',
                         data=self.data,
                         portal_type='ftw.mail.mail')
        return result['success']

    def with_message(self, data, filename=None):
        self.data = data
        if filename:
            self.filename = filename
        return self

    def with_asset_message(self, filename):
        self.with_message(assets.load(filename), unicode(filename))
        return self

builder_registry.register('quickuploaded_mail', QuickuploadMailBuilder)


class QuickuploadDocumentBuilder(PloneObjectBuilder):

    def __init__(self, session):
        super(QuickuploadDocumentBuilder, self).__init__(session)
        self.data = None
        self.filename = 'document.txt'
        self.content_type = 'text/plain'

    def create_object(self, **kwargs):
        factory = getAdapter(self.container, IQuickUploadFileFactory)
        assert factory, 'invalid container'

        result = factory(filename=self.filename,
                         title='',  # ignored by adapter
                         description=None,
                         content_type=self.content_type,
                         data=self.data,
                         portal_type='opengever.document.document')

        return result['success']

    def with_data(self, data, filename=None, content_type=None):
        self.data = data
        if filename:
            self.filename = filename
        if content_type:
            self.content_type = content_type
        return self

    def with_asset_data(self, filename, content_type=None):
        self.with_data(assets.load(filename), unicode(filename),
                       content_type=content_type)
        if not content_type:
            extension = os.path.splitext(filename)[1]
            content_type = mimetypes.types_map.get(extension)
        return self

builder_registry.register('quickuploaded_document', QuickuploadDocumentBuilder)
