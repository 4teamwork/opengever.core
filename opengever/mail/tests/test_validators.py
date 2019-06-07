from ftw.builder import Builder
from ftw.builder import create
from ftw.mail.mail import IMail
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import assert_no_error_messages
from ftw.testing import MockTestCase
from opengever.core.testing import COMPONENT_UNIT_TESTING
from opengever.mail.interfaces import ISendDocumentConf
from opengever.mail.validators import AddressValidator
from opengever.mail.validators import DocumentSizeValidator
from opengever.mail.validators import FilesTooLarge
from opengever.testing import FunctionalTestCase
from opengever.testing import OPENGEVER_FUNCTIONAL_TESTING
from plone.registry.interfaces import IRegistry
from zope.interface import Invalid
from zope.schema.interfaces import RequiredMissing


class TestValidators(MockTestCase):
    layer = COMPONENT_UNIT_TESTING

    def test_document_size_validator(self):

        context = self.stub()
        request = self.stub()
        mail1 = self.providing_stub([IMail])
        doc1 = self.stub()
        self.expect(mail1.message.getSize()).result(300000)
        self.expect(doc1.file.getSize()).result(800000)
        documents = [mail1, doc1]

        registry = self.stub()
        reg_proxy = self.stub()
        self.mock_utility(registry, IRegistry)
        self.expect(registry.forInterface(ISendDocumentConf)).result(reg_proxy)

        with self.mocker.order():
            # 3:
            self.expect(
                request.get('form.widgets.documents_as_links')).result([None, ])
            self.expect(reg_proxy.max_size).result(5)

            # 4:
            self.expect(
                request.get('form.widgets.documents_as_links')).result([None, ])
            self.expect(reg_proxy.max_size).result(1)

            # 5:
            self.expect(
                request.get('form.widgets.documents_as_links')).result(['selected', ])
            self.expect(reg_proxy.max_size).result(1)

        self.replay()

        validator = DocumentSizeValidator(
            context, request, None, None, None)

        # 1: No value
        with self.assertRaises(RequiredMissing):
            validator.validate(None)

        # 2: empty list as value
        with self.assertRaises(RequiredMissing):
            validator.validate([])

        # 3: with a valid complete size
        validator.validate(documents)

        # 4: with an invalid complete size
        with self.assertRaises(FilesTooLarge):
            validator.validate(documents)

        # 5: with an invalid complete size, but we send only the links
        validator.validate(documents)

    def test_address_validator(self):
        context = self.stub()
        request = self.stub_request()

        self.replay()

        validator = AddressValidator(context, request, None, None, None)
        validator.validate(['hugo.boss@example.org', 'James.Bond@example.org'])

        with self.assertRaises(Invalid):
            validator.validate(['hugo.boss@example.com', 'James.Example.com'])

        with self.assertRaises(Invalid):
            validator.validate(['hugo.dskljfch', 'James.Example.com'])


class TestFileOrPaperValidatorInEditForm(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestFileOrPaperValidatorInEditForm, self).setUp()

        self.dossier = create(Builder('dossier'))
        self.mail = create(Builder('mail')
                                   .within(self.dossier)
                                   .with_dummy_message())

    @browsing
    def test_editing_and_saving_valid_mail_works(self, browser):
        browser.login().open(self.mail, view='edit')
        assert_no_error_messages()

    @browsing
    def test_mail_preserved_as_paper_is_valid(self, browser):
        browser.login().open(self.mail, view='edit')
        browser.fill({'Preserved as paper': True}).save()
        self.assertTrue(self.mail.preserved_as_paper)
        assert_no_error_messages()

    @browsing
    def test_mail_not_preserved_as_paper_is_valid(self, browser):
        browser.login().open(self.mail, view='edit')
        browser.fill({'Preserved as paper': False}).save()
        self.assertFalse(self.mail.preserved_as_paper)
        assert_no_error_messages()
