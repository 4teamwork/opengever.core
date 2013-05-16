import transaction
from plone.dexterity.utils import createContentInContainer
from plone.app.testing import TEST_USER_ID
from opengever.testing import FunctionalTestCase

from opengever.testing import create_client
from opengever.testing import set_current_client_id
from opengever.testing import create_ogds_user

class TestSearchWithContent(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestSearchWithContent, self).setUp()

        create_client()
        set_current_client_id(self.layer['portal'])
        create_ogds_user(TEST_USER_ID)

        self.dossier1 = createContentInContainer(self.portal,
                                                 'opengever.dossier.businesscasedossier',
                                                 title='Dossier1', checkConstraints=False)
        self.dossier2 = createContentInContainer(self.portal,
                                                 'opengever.dossier.businesscasedossier',
                                                 title='Dossier2', checkConstraints=False)
        transaction.commit()


    def test_search_dossiers(self):
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "dossier1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.dossier.behaviors.dossier.IDossierMarker']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertSearchResultCount(1)

        self.browser.open('http://nohost/plone/@@search?object_provides=opengever.dossier.behaviors.dossier.IDossierMarker&SearchableText=dossier1')


    def test_search_documents(self):
        createContentInContainer(self.dossier1,
                                 'opengever.document.document',
                                 title='Document1', checkConstraints=False)
        createContentInContainer(self.dossier2,
                                 'opengever.document.document',
                                 title='Document2', checkConstraints=False)
        transaction.commit()

        # search documents (we can't find the document because we must change the content-type)
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "document1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.dossier.behaviors.dossier.IDossierMarker']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertSearchResultCount(0)
        self.browser.open('http://nohost/plone/@@search?object_provides=opengever.dossier.behaviors.dossier.IDossierMarker&SearchableText=document1')


        # search documents with the right content-type
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "(document1)"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.document.behaviors.IBaseDocument']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.browser.open('http://nohost/plone/@@search?object_provides=opengever.document.behaviors.IBaseDocument&SearchableText=document1')
        self.assertSearchResultCount(1)

    def test_search_tasks(self):
        createContentInContainer(self.dossier1,
                                 'opengever.task.task',
                                 title='Task1', checkConstraints=False)
        createContentInContainer(self.dossier2,
                                 'opengever.task.task',
                                 title='Task2', checkConstraints=False)
        transaction.commit()

        # search tasks (we can't find the task because we must change the content-type)
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "task1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.document.behaviors.IBaseDocument']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertSearchResultCount(0)
        self.browser.open('http://nohost/plone/@@search?object_provides=opengever.document.behaviors.IBaseDocument&SearchableText=task1')


        # search tasks with the right content-type
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "task1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.task.task.ITask']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertSearchResultCount(1)
        self.browser.open('http://nohost/plone/@@search?object_provides=opengever.task.task.ITask&SearchableText=task1')

    def assertSearchResultCount(self, count):
        self.assertEquals(str(count), self.css("#search-results-number")[0].text)


class TestSearchWithoutContent(FunctionalTestCase):
    use_browser = True

    def setUp(self):
        super(TestSearchWithoutContent, self).setUp()

        create_client()
        set_current_client_id(self.layer['portal'])
        create_ogds_user(TEST_USER_ID)

        self.dossier1 = createContentInContainer(self.portal,
             'opengever.dossier.businesscasedossier',
             title='Dossier1', checkConstraints=False)

        transaction.commit()

    def test_validate_searchstring_for_dossiers(self):
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "dossier1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.dossier.behaviors.dossier.IDossierMarker']
        self.browser.getControl(name='form.widgets.start_1').value = "1/1/10"
        self.browser.getControl(name='form.widgets.start_2').value = "2/1/10"
        self.browser.getControl(name='form.widgets.end_1').value = "3/1/10"
        self.browser.getControl(name='form.widgets.end_2').value = "4/1/10"
        self.browser.getControl(name='form.widgets.reference').value = "OG 14.2"
        self.browser.getControl(name='form.widgets.sequence_number').value = "5"
        self.browser.getControl(name='form.widgets.searchable_filing_no').value = "14"
        self.browser.getControl(name='form.widgets.dossier_review_state:list').value = ['dossier-state-active']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertCurrentUrl('http://nohost/plone/@@search?object_provides=opengever.dossier.behaviors.dossier.IDossierMarker&SearchableText=dossier1&start_usage=range:minmax&start:list=01/01/10&start:list=02/02/10&end_usage=range:minmax&end:list=03/01/10&end:list=04/02/10&reference=OG%2014.2&sequence_number:int=5&searchable_filing_no=14&review_state:list=dossier-state-active')

    def test_validate_searchstring_for_documents(self):
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "document1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.document.behaviors.IBaseDocument']
        self.browser.getControl(name='form.widgets.receipt_date_1').value = "1/1/10"
        self.browser.getControl(name='form.widgets.receipt_date_2').value = "2/1/10"
        self.browser.getControl(name='form.widgets.delivery_date_1').value = "3/1/10"
        self.browser.getControl(name='form.widgets.delivery_date_2').value = "4/1/10"
        self.browser.getControl(name='form.widgets.document_author').value = "Eduard"
        self.browser.getControl(name='form.widgets.trashed:list').value = True
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertCurrentUrl('http://nohost/plone/@@search?object_provides=opengever.document.behaviors.IBaseDocument&SearchableText=document1&receipt_date_usage=range:minmax&receipt_date:list=01/01/10&receipt_date:list=02/02/10&delivery_date_usage=range:minmax&delivery_date:list=03/01/10&delivery_date:list=04/02/10&document_author=Eduard&trashed:list:boolean=True&trashed:list:boolean=False')

    def test_validate_searchstring_for_tasks(self):
        self.browser.open('%s/advanced_search' % self.dossier1.absolute_url())
        self.browser.getControl(name='form.widgets.searchableText').value = "task1"
        self.browser.getControl(name='form.widgets.object_provides:list').value = ['opengever.task.task.ITask']
        self.browser.getControl(name='form.widgets.deadline_1').value = "1/1/10"
        self.browser.getControl(name='form.widgets.deadline_2').value = "1/1/10"
        self.browser.getControl(name='form.widgets.task_type:list').value = ['information']
        self.browser.getControl(name='form.widgets.dossier_review_state:list').value = ['dossier-state-active']
        self.browser.getControl(name='form.buttons.button_search').click()
        self.assertCurrentUrl('http://nohost/plone/@@search?object_provides=opengever.task.task.ITask&SearchableText=task1&deadline_usage=range:minmax&deadline:list=01/01/10&deadline:list=01/02/10&task_type=information')

    def test_disable_unload_protection(self):
        self.browser.open('%s/advanced_search' %(self.portal.absolute_url()))
        self.assertPageContainsNot('enableUnloadProtection')
