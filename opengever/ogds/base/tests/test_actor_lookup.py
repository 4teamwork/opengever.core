from ftw.builder import Builder
from ftw.builder import create
from opengever.ogds.base.actor import Actor
from opengever.testing import FunctionalTestCase


class TestActorLookup(FunctionalTestCase):

    def setUp(self):
        super(TestActorLookup, self).setUp()
        self.grant('Reader', 'Contributor')

    def test_null_actor(self):
        actor = Actor.lookup(None)

        self.assertEqual('', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertIsNone(actor.get_link())

    def test_inbox_actor_lookup(self):
        create(Builder('org_unit').id('foobar').having(title='Huhu'))
        actor = Actor.lookup('inbox:foobar')

        self.assertEqual('Inbox: Huhu', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('Inbox: Huhu', actor.get_link())

    def test_contact_actor_lookup(self):
        contact = create(Builder('contact')
                         .having(firstname=u'Hanspeter',
                                 lastname=u'Blahbla',
                                 email='h@example.com')
                         .in_state('published'))
        actor = Actor.lookup('contact:{}'.format(contact.id))
        self.assertEqual('Blahbla Hanspeter (h@example.com)',
                         actor.get_label())
        self.assertEqual(contact.absolute_url(), actor.get_profile_url())

        link = actor.get_link()
        self.assertIn(actor.get_label(), link)
        self.assertIn(actor.get_profile_url(), link)

    def test_user_actor_ogds_user(self):
        create(Builder('fixture').with_hugo_boss())
        actor = Actor.lookup('hugo.boss')

        self.assertEqual('Boss Hugo (hugo.boss)', actor.get_label())
        self.assertTrue(
            actor.get_profile_url().endswith('@@user-details/hugo.boss'))

        link = actor.get_link()
        self.assertIn(actor.get_label(), link)
        self.assertIn(actor.get_profile_url(), link)
