from opengever.ogds.base.actor import Actor
from opengever.testing import IntegrationTestCase


class TestActorLookup(IntegrationTestCase):

    def test_null_actor(self):
        actor = Actor.lookup('not-existing')
        self.assertEqual('not-existing', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual('not-existing', actor.get_link())

    def test_inbox_actor_lookup(self):
        actor = Actor.lookup('inbox:fa')

        self.assertEqual(u'Inbox: Finanz\xe4mt', actor.get_label())
        self.assertIsNone(actor.get_profile_url())
        self.assertEqual(u'Inbox: Finanz\xe4mt', actor.get_link())
        self.assertEqual(u'fa_inbox_users', actor.permission_identifier)
        self.assertEqual(
            u'<span class="actor-label actor-inbox">Inbox: Finanz\xe4mt</span>',
            actor.get_link(with_icon=True))

    def test_contact_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('contact:{}'.format(self.franz_meier.id))

        self.assertEqual('Meier Franz (meier.f@example.com)',
                         actor.get_label())
        self.assertEqual(self.franz_meier.absolute_url(),
                         actor.get_profile_url())

        link = actor.get_link(with_icon=True)
        self.assertIn(actor.get_label(), link)
        self.assertIn(actor.get_profile_url(), link)
        self.assertIn('class="actor-label actor-contact"', link)

    def test_team_actor_lookup(self):
        self.login(self.regular_user)
        actor = Actor.lookup('team:1')

        self.assertEqual(u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)',
                         actor.get_label())
        self.assertEqual('http://nohost/plone/kontakte/team-1/view',
                         actor.get_profile_url())

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/team-1/view" '
            u'class="actor-label actor-team">Projekt \xdcberbaung Dorfmatte '
            u'(Finanz\xe4mt)</a>',
            actor.get_link(with_icon=True))

        self.assertEqual(
            u'<a href="http://nohost/plone/kontakte/team-1/view">'
            u'Projekt \xdcberbaung Dorfmatte (Finanz\xe4mt)</a>',
            actor.get_link())

    def test_user_actor_ogds_user(self):
        actor = Actor.lookup('jurgen.konig')

        self.assertEqual(
            u'K\xf6nig J\xfcrgen (jurgen.konig)', actor.get_label())
        self.assertEqual('jurgen.konig', actor.permission_identifier)
        self.assertTrue(
            actor.get_profile_url().endswith('@@user-details/jurgen.konig'))

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/jurgen.konig">'
            u'K\xf6nig J\xfcrgen (jurgen.konig)</a>',
            actor.get_link())

        self.assertEqual(
            u'<a href="http://nohost/plone/@@user-details/jurgen.konig" '
            u'class="actor-label actor-user">K\xf6nig J\xfcrgen '
            u'(jurgen.konig)</a>',
            actor.get_link(with_icon=True))

    def test_get_link_returns_safe_html(self):
        self.login(self.regular_user)

        self.franz_meier.firstname = u"Foo <b onmouseover=alert('Foo!')>click me!</b>"
        self.franz_meier.reindexObject()
        actor = Actor.lookup('contact:meier-franz')

        self.assertEquals(
            u'<a href="http://nohost/plone/kontakte/meier-franz">'
            u'Meier Foo &lt;b onmouseover=alert(&apos;Foo!&apos;)&gt;click me!&lt;/b&gt; (meier.f@example.com)'
            u'</a>',
            actor.get_link())


class TestActorCorresponding(IntegrationTestCase):

    def test_user_corresponds_to_current_user(self):
        actor = Actor.lookup('jurgen.konig')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))

    def test_inbox_corresponds_to_all_inbox_assigned_users(self):
        actor = Actor.lookup('inbox:fa')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))

    def test_team_corresponds_to_all_team_group_members(self):
        actor = Actor.lookup('team:1')

        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.regular_user)))
        self.assertTrue(
            actor.corresponds_to(self.get_ogds_user(self.dossier_responsible)))
        self.assertFalse(
            actor.corresponds_to(self.get_ogds_user(self.secretariat_user)))


class TestActorRepresentatives(IntegrationTestCase):

    def test_user_is_the_only_representatives_of_a_user(self):
        actor = Actor.lookup('jurgen.konig')
        self.assertEquals([self.get_ogds_user(self.secretariat_user)],
                          actor.representatives())

        actor = Actor.lookup(self.regular_user.getId())
        self.assertEquals([self.get_ogds_user(self.regular_user)],
                          actor.representatives())

    def test_all_users_of_the_inbox_group_are_inbox_representatives(self):
        actor = Actor.lookup('inbox:fa')
        self.assertItemsEqual(
            [self.get_ogds_user(self.secretariat_user)],
            actor.representatives())

    def test_contact_has_no_representatives(self):
        actor = Actor.lookup('contact:meier-franz')
        self.assertItemsEqual([], actor.representatives())

    def test_all_group_members_are_team_representatives(self):
        actor = Actor.lookup('team:1')
        self.assertItemsEqual(
            [self.get_ogds_user(self.regular_user),
             self.get_ogds_user(self.dossier_responsible)],
            actor.representatives())


class TestActorPermissionIdentifier(IntegrationTestCase):

    def test_groupid_is_team_actors_permission_identifier(self):
        actor = Actor.lookup('team:1')

        self.assertEquals('projekt_a', actor.permission_identifier)
