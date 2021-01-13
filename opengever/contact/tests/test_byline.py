from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestContactByline(FunctionalTestCase):

    def setUp(self):
        super(TestContactByline, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))

    @browsing
    def test_contains_contact_id_as_sequence_number(self, browser):
        person = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'M\xfcller'))
        organization = create(Builder('organization')
                              .having(name=u'Meier AG'))

        browser.login().open(self.contactfolder, view=person.wrapper_id)
        self.assertEquals(
            ['Sequence number: 1'],
            browser.css('#plone-document-byline .sequenceNumber').text)

        browser.open(self.contactfolder, view=organization.wrapper_id)
        self.assertEquals(
            ['Sequence number: 2'],
            browser.css('#plone-document-byline .sequenceNumber').text)

    @browsing
    def test_is_active_value_is_yes_or_no(self, browser):
        person1 = create(Builder('person')
                         .having(firstname=u'Peter', lastname=u'M\xfcller'))
        person2 = create(Builder('person')
                         .having(firstname=u'Peter', lastname=u'M\xfcller',
                                 is_active=False))

        organization1 = create(Builder('organization')
                               .having(name=u'Meier AG'))
        organization2 = create(Builder('organization')
                               .having(name=u'Meier AG', is_active=False))

        browser.login().open(self.contactfolder, view=person1.wrapper_id)
        self.assertEquals(['Active: Yes'],
                          browser.css('#plone-document-byline .active').text)

        browser.open(self.contactfolder, view=person2.wrapper_id)
        self.assertEquals(['Active: No'],
                          browser.css('#plone-document-byline .active').text)

        browser.open(self.contactfolder, view=organization1.wrapper_id)
        self.assertEquals(['Active: Yes'],
                          browser.css('#plone-document-byline .active').text)

        browser.open(self.contactfolder, view=organization2.wrapper_id)
        self.assertEquals(['Active: No'],
                          browser.css('#plone-document-byline .active').text)

    @browsing
    def test_displays_former_contact_id_if_exists(self, browser):
        person1 = create(Builder('person')
                         .having(firstname=u'Peter', lastname=u'M\xfcller',
                                 former_contact_id=123))
        person2 = create(Builder('person')
                         .having(firstname=u'Peter', lastname=u'M\xfcller',
                                 is_active=False))

        organization1 = create(Builder('organization')
                               .having(name=u'Meier AG',
                                       former_contact_id=345))
        organization2 = create(Builder('organization')
                               .having(name=u'Meier AG', is_active=False))

        browser.login().open(self.contactfolder, view=person1.wrapper_id)
        self.assertEquals(
            ['Former contact ID: 123'],
            browser.css('#plone-document-byline .former_contact_id').text)

        browser.open(self.contactfolder, view=person2.wrapper_id)
        self.assertEquals(
            [], browser.css('#plone-document-byline .former_contact_id').text)

        browser.login().open(self.contactfolder, view=organization1.wrapper_id)
        self.assertEquals(
            ['Former contact ID: 345'],
            browser.css('#plone-document-byline .former_contact_id').text)

        browser.open(self.contactfolder, view=organization2.wrapper_id)
        self.assertEquals(
            [], browser.css('#plone-document-byline .former_contact_id').text)
