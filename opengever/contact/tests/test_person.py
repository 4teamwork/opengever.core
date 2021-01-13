from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages.statusmessages import info_messages
from opengever.contact.models.person import Person
from opengever.testing import FunctionalTestCase


class TestPerson(FunctionalTestCase):

    def test_get_url_returns_url_for_wrapper_object(self):
        create(Builder('contactfolder'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        sandra = create(Builder('person')
                        .having(firstname=u'Sandra', lastname=u'Meier'))

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/contact-1/view',
            peter.get_url())
        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/contact-2/edit',
            sandra.get_url(view='edit'))

    @browsing
    def test_person_can_be_added_in_browser(self, browser):
        contactfolder = create(Builder('contactfolder'))

        browser.login().open(contactfolder, view="@@add-person")

        browser.fill({'Salutation': u'Sir',
                      'Academic title': u'Dr',
                      'First name': u'Hanspeter',
                      'Last name': u'Hansj\xf6rg',
                      'Description': u'Pellentesque posuere.'}).submit()

        self.assertEquals([u'Record created'], info_messages())

        person = Person.query.first()
        self.assertIsNotNone(person)

        self.assertEqual(u'Sir', person.salutation)
        self.assertEqual(u'Dr', person.academic_title)
        self.assertEqual(u'Hanspeter', person.firstname)
        self.assertEqual(u'Hansj\xf6rg', person.lastname)
        self.assertEqual(u'Pellentesque posuere.', person.description)

    @browsing
    def test_person_can_be_edited_in_browser(self, browser):
        contactfolder = create(Builder('contactfolder'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        browser.login().open(contactfolder, view=peter.wrapper_id)

        browser.find("Edit").click()

        browser.fill({'Salutation': u'Sir',
                      'Academic title': u'Dr',
                      'First name': u'Hanspeter',
                      'Last name': u'Hansj\xf6rg',
                      'Description': u'Pellentesque posuere.'}).submit()

        self.assertEquals([u'Changes saved'], info_messages())

        person = Person.get(peter.person_id)
        self.assertIsNotNone(person)
        self.assertEqual(u'Sir', person.salutation)
        self.assertEqual(u'Dr', person.academic_title)
        self.assertEqual(u'Hanspeter', person.firstname)
        self.assertEqual(u'Hansj\xf6rg', person.lastname)
        self.assertEqual(u'Pellentesque posuere.', person.description)

    def test_get_by_former_contact_id_returns_contact(self):
        peter = create(Builder('person')
                       .having(
                           firstname=u'Peter',
                           lastname=u'M\xfcller',
                           former_contact_id=13))

        self.assertEqual(peter, Person.query.get_by_former_contact_id(13))

    def test_get_by_former_contact_id_returns_none_if_no_contact_available(self):
        self.assertIsNone(Person.query.get_by_former_contact_id(13))
