from opengever.ogds.base.autocomplete_widget import AutocompleteFieldWidget
from opengever.ogds.base.setuphandlers import _create_example_user, _create_example_client
from opengever.ogds.base.utils import create_session
from opengever.task.task import ITask
from opengever.testing import FunctionalTestCase
from opengever.testing import set_current_client_id
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.indexer.interfaces import IIndexer
from plone.memoize import volatile
from zope.component import getUtility
from zope.component import provideAdapter
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory


class TestAutoCompleteWidget(FunctionalTestCase):

    def test_widget(self):
        set_current_client_id(self.portal)

        # Lets set up some users and clients for testing the vocabularies with:
        session = create_session()


        # Mocked containging_dossier indexer
        class MockedIndexer(object):
            def __init__(self, context, catalog):
                pass

            def __call__(self):
                    return 'Peter'
        provideAdapter(factory=MockedIndexer, adapts=[Interface, Interface],
                provides=IIndexer, name='containing_dossier')

        # Users:
        _create_example_user(session, self.portal,
                                  'hugo.boss',
                                  {'firstname': 'Hugo',
                                  'lastname': 'Boss'},
                                 ('og_mandant1_users',))

        _create_example_user(session, self.portal,
                                 'franz.michel',
                                 {'firstname': 'Franz',
                                  'lastname': 'Michel'},
                                 ('og_mandant1_users',
                                  'og_mandant2_users'))


        _create_example_client(session, 'client1',
                                      {'title': 'client1',
                                      'ip_address': '127.0.0.1',
                                      'site_url': 'http://nohost/plone',
                                      'public_url': 'http://nohost/plone',
                                      'group': 'og_mandant1_users',
                                      'inbox_group': 'og_mandant1_inbox'})


        # we create example task
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Manager'])
        id = self.portal.invokeFactory('opengever.task.task', 'task-1')
        task1 = self.portal[id]

        # We bind task (as context) to ``AutocompleteFieldWidget`` widget.
        field = ITask['issuer']
        widget = AutocompleteFieldWidget(field, self.portal.REQUEST)
        widget.context = task1

        # Let's clear the cache of the vocabulary first:

        fact = getUtility(IVocabularyFactory,
                               name='opengever.ogds.base.ContactsAndUsersVocabulary')
        setattr(fact, volatile.ATTR, {})


        # Initialy we dont have any value for our ``ITask.issuer`` field, thats why we
        # also don't hide anything.
        source = widget.bound_source
        self.assertEquals(
            [u'hugo.boss', u'franz.michel', u'inbox:client1'],
            [i.value for i in source])

        self.assertEquals([], source.hidden_terms)

        # Then we set our example task to some value which is not existing in used
        # vocabulary and we set ``widget._bound_source`` to None so source will be
        # initialized again.
        task1.issuer = u'test1'
        widget._bound_source = None

        # Now we can see that value set before does not show in listing, but its
        # added to hidden list of terms.
        source2 = widget.bound_source
        self.assertEquals(
            [u'hugo.boss', u'franz.michel', u'inbox:client1'],
            [i.value for i in source2])

        self.assertEquals([u'test1'], source2.hidden_terms)
