from Products.CMFCore.utils import getToolByName
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain


class TestContact(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestContact, self).setUp()
        self.grant('Member', 'Contributor', 'Manager')

    def getSearchableText(self, obj):
        brain = obj2brain(obj)
        catalog = getToolByName(obj, 'portal_catalog')
        data = catalog.getIndexDataForRID(brain.getRID())
        return data['SearchableText']

    def test_browser(self):
        self.browser.open(self.portal.portal_url())
        self.assertPageContains('test_user_1')

        # create a contact folder
        self.browser.open('http://nohost/plone/folder_factories')
        self.browser.getControl('ContactFolder').click()
        self.browser.getControl('Add').click()
        self.browser.assert_url('http://nohost/plone/++add++opengever.contact.contactfolder')
        self.browser.getControl('Title').value='Foobar'
        self.browser.getControl('Description').value='Lorem Ipsum'
        self.browser.getControl('Save').click()

        # create a contact:
        self.browser.open('http://nohost/plone/foobar/folder_factories')
        self.browser.getControl('Contact').click()
        self.browser.getControl('Add').click()

        self.browser.assert_url('http://nohost/plone/foobar/++add++opengever.contact.contact')
        self.browser.getControl('Firstname').value = 'lorem'
        self.browser.getControl('Save').click()

        self.browser.assert_url('http://nohost/plone/foobar/++add++opengever.contact.contact')

        self.browser.getControl('Firstname').value = 'Hanspeter'
        self.browser.getControl('Lastname').value = 'Walter'
        self.browser.getControl('Description').value = 'Lorem ipsum, bla bla'
        self.browser.getControl('Save').click()
        self.browser.assert_url('http://nohost/plone/foobar/walter-hanspeter/contact_view')

        # test searchabelText indexing
        obj = self.portal.get('foobar').get('walter-hanspeter')
        self.assertEquals(['walter', 'hanspeter'], self.getSearchableText(obj))

        folder = self.portal.get('foobar')
        self.assertEquals('Foobar', folder.Title())
        self.assertEquals('Lorem Ipsum', folder.Description())

        contact = folder.get('walter-hanspeter')
        self.assertEquals('Walter Hanspeter', contact.Title())
        self.assertEquals('Lorem ipsum, bla bla', contact.Description())
