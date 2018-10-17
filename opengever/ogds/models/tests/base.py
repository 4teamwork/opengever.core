from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import MEMORY_DB_LAYER
from opengever.ogds.models.service import OGDSService
import unittest2


class OGDSTestCase(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    @property
    def session(self):
        return self.layer.session

    def setUp(self):
        super(OGDSTestCase, self).setUp()

        self.service = OGDSService(self.session)

        self.john = create(
            Builder("ogds_user").id("john").having(firstname="John", lastname="Smith", email="j.smith@example.org")
        )

        self.hugo = create(
            Builder("ogds_user").id("hugo").having(firstname="Hugo", lastname="Boss", email="h.boss@example.org")
        )

        self.peter = create(
            Builder("ogds_user").id("peter").having(firstname="Peter", lastname=u"Zw\xf6imeter", email="2@example.org")
        )

        self.jack = create(Builder("ogds_user").id("jack").having(lastname="Smith", email="smith@example.org"))
        self.bob = create(Builder("ogds_user").id("bob").having(firstname="Bob", email="bob@example.org", active=False))
        self.admin = create(Builder("ogds_user").id("admin").having(active=False))

        self.members_a = create(Builder("ogds_group").id("members_a").having(users=[self.john, self.hugo]))
        self.members_b = create(Builder("ogds_group").id("members_b").having(users=[self.peter, self.hugo]))
        self.members_c = create(Builder("ogds_group").id("members_c").having(users=[self.jack]))
        self.inbox_members = create(Builder("ogds_group").id("inbox_members").having(users=[self.john, self.peter]))
        self.inactive_members = create(Builder("ogds_group").id("sondergruppe").having(active=False))

        self.org_unit_a = create(
            Builder("org_unit")
            .id("unita")
            .having(title="Unit A", users_group=self.members_a, inbox_group=self.inbox_members, admin_unit_id="canton_1")
        )

        self.org_unit_b = create(
            Builder("org_unit").id("unitb").having(title="Unit B", users_group=self.members_b, admin_unit_id="canton_2")
        )

        self.org_unit_c = create(
            Builder("org_unit").id("unitc").having(title="Unit C", users_group=self.members_c, admin_unit_id="other")
        )

        self.org_unit_d = create(
            Builder("org_unit").id("unitd").having(title="Unit D", admin_unit_id="other", enabled=False)
        )

        self.admin_unit_1 = create(
            Builder("admin_unit")
            .id("canton_1")
            .having(title="Canton 1 Unit")
            .assign_org_units([self.org_unit_a, self.org_unit_b])
        )

        self.admin_unit_2 = create(Builder("admin_unit").id("canton_2").having(title="Canton 2 Unit"))
        self.admin_unit_3 = create(Builder("admin_unit").id("canton_3").having(title="Canton 3 Unit", enabled=False))

        self.inbox = self.org_unit_a.inbox()
