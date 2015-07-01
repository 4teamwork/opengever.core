from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import builder_registry
from ftw.builder import PloneObjectBuilder
from opengever.testing import assets


class QuickuploadMailBuilder(PloneObjectBuilder):

    def __init__(self, session):
        super(QuickuploadMailBuilder, self).__init__(session)
        self.data = None

    def create_object(self, **kwargs):
        factory = IQuickUploadFileFactory(self.container)
        assert factory, 'invalid container'

        result = factory(filename='mail.eml',
                         title='',  # ignored by adapter
                         description='',  # ignored by adapter
                         content_type='message/rfc822',
                         data=self.data,
                         portal_type='ftw.mail.mail')
        return result['success']

    def with_message(self, data):
        self.data = data

    def with_asset_message(self, filename):
        self.with_message(assets.load(filename), unicode(filename))
        return self

builder_registry.register('quickuploaded_mail', QuickuploadMailBuilder)
