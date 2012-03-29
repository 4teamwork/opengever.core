from collective.quickupload.browser.interfaces import IQuickUploadFileFactory
from mocker import ANY
from ftw.tabbedview.interfaces import ITabbedviewUploadable
from ftw.testing import MockTestCase
from grokcore.component.testing import grok, grok_component
from plone.directives import form
from plone.namedfile.field import NamedFile as nf_field
from plone.namedfile.file import NamedFile
from unittest2 import TestCase
from zope import schema
import zope.component.testing


class ITest1(form.Schema):
    title = schema.TextLine(
        title=u'label_title',
        required=False)

    description = schema.Text(
        title=u'description',
        default=u'hanspeter',
        required=False,
        )


class ITest2(form.Schema):
    form.primary('file')
    file = nf_field(
        title=u'label_file',
        required=False,
        )


class TestOGQuickupload(MockTestCase, TestCase):

    def setUp(self):
        grok('plone.directives.form.meta')
        grok('opengever.base.quickupload')

    def tearDown(self):
        zope.component.testing.tearDown()

    def test_get_mimetype(self):
        mock_context = self.providing_stub([ITabbedviewUploadable])
        self.replay()
        adapter = IQuickUploadFileFactory(mock_context)
        self.assertEqual(adapter.get_mimetype('hanspeter.doc'),
            'application/msword')

        self.assertEqual(adapter.get_mimetype('hanspeter.jpeg'),
            'image/jpeg')

    def test_get_portal_type(self):
        mock_context = self.providing_stub([ITabbedviewUploadable])
        self.replay()
        adapter = IQuickUploadFileFactory(mock_context)

        self.assertEqual(
            adapter.get_portal_type('image/jpeg'), 'opengever.document.document')
        self.assertEqual(
            adapter.get_portal_type('message/rfc822'), 'ftw.mail.mail')
        self.assertEqual(
            adapter.get_portal_type('application/ msword'),
            'opengever.document.document')

    def test_set_default_value(self):
        grok_component('ITest2', ITest2)

        # mock stuf
        mock_context = self.providing_stub([ITabbedviewUploadable,])
        named_file = NamedFile('bla bla', filename=u'test.txt')

        obj = self.providing_stub([ITest1, ITest2])
        request = self.stub()
        self.expect(obj.REQUEST).result(request)

        iterSchemata = self.mocker.replace(
            'plone.dexterity.utils.iterSchemata')
        self.expect(iterSchemata(obj)).result([ITest1, ITest2])

        self.replay()

        # test if it's sets the default value and
        # also if it add the created file to the primary field
        adapter = IQuickUploadFileFactory(mock_context)
        adapter.set_default_values(obj, named_file)
        self.assertEquals(obj.description, 'hanspeter')
        self.assertEquals(obj.file, named_file)

    def test_create_file(self):
        grok_component('ITest2', ITest2)

        # mock stuf
        mock_context = self.providing_stub([ITabbedviewUploadable,])
        named_file = NamedFile('bla bla', filename=u'test.txt')

        obj = self.providing_stub([ITest1, ITest2])
        request = self.stub()
        self.expect(obj.REQUEST).result(request)

        iterSchemata = self.mocker.replace(
            'plone.dexterity.utils.iterSchemata')
        self.expect(iterSchemata(obj)).result([ITest1, ITest2])

        self.replay()

        # test if it's sets the default value and
        # also if it add the created file to the primary field
        adapter = IQuickUploadFileFactory(mock_context)
        named_file = adapter.create_file(
            u'hugo.jpeg', u'data data', u'image/jpeg', obj)

        self.assertEquals(named_file.data, u'data data')

    def test_complete_creation(self):
        grok_component('ITest2', ITest2)

        # mock stuf
        mock_context = self.providing_stub([ITabbedviewUploadable,])

        obj = self.providing_stub([ITest1, ITest2])
        request = self.stub()
        self.expect(obj.REQUEST).result(request)
        self.expect(obj.reindexObject()).result(None)

        iterSchemata = self.mocker.replace(
            'plone.dexterity.utils.iterSchemata')
        self.expect(iterSchemata(obj)).result([ITest1, ITest2]).count(0, None)

        createContentInContainer = self.mocker.replace(
            'plone.dexterity.utils.createContentInContainer')
        self.expect(createContentInContainer(
                mock_context, 'opengever.document.document')).result(obj)

        # filedata
        filename = u'hugo.doc'
        title = None
        description  = None
        content_type = None
        data = u'Data data'
        portal_type = None

        self.replay()

        adapter = IQuickUploadFileFactory(mock_context)
        result = adapter(filename, title, description, content_type, data, portal_type)
        obj = result.get('success')
        self.assertEquals(obj.description, 'hanspeter')
        self.assertEquals(obj.file.data, u'Data data')
