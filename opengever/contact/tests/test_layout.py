from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPersonLayout(FunctionalTestCase):

    def setUp(self):
        super(TestPersonLayout, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))

    @browsing
    def test_body_contains_person_type_class(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertIn('portaltype-opengever-contact-person',
                      browser.css('body').first.get('class'))

    @browsing
    def test_body_contains_state_class(self, browser):
        active = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'Meier'))
        inactive = create(Builder('person')
                          .having(firstname=u'Peter', lastname=u'Meier',
                                  is_active=False))

        browser.login().open(self.contactfolder, view=active.wrapper_id)
        self.assertIn('state-active', browser.css('body').first.get('class'))

        browser.login().open(self.contactfolder, view=inactive.wrapper_id)
        self.assertIn('state-inactive', browser.css('body').first.get('class'))


class TestOrganizationLayout(FunctionalTestCase):

    def setUp(self):
        super(TestOrganizationLayout, self).setUp()
        self.contactfolder = create(Builder('contactfolder'))

    @browsing
    def test_body_contains_person_type_class(self, browser):
        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        browser.login().open(self.contactfolder, view=peter.wrapper_id)
        self.assertIn('portaltype-opengever-contact-person',
                      browser.css('body').first.get('class'))

    @browsing
    def test_body_contains_state_class(self, browser):
        active = create(Builder('person')
                        .having(firstname=u'Peter', lastname=u'Meier'))
        inactive = create(Builder('person')
                          .having(firstname=u'Peter', lastname=u'Meier',
                                  is_active=False))

        browser.login().open(self.contactfolder, view=active.wrapper_id)
        self.assertIn('state-active', browser.css('body').first.get('class'))

        browser.login().open(self.contactfolder, view=inactive.wrapper_id)
        self.assertIn('state-inactive', browser.css('body').first.get('class'))
