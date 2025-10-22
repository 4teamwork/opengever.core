from opengever.ogds.models.group import Group
from opengever.ogds.models.group_membership import GroupMembership
from opengever.ogds.models.tests.base import OGDSTestCase
from opengever.ogds.models.user import User
from sqlalchemy.orm import selectinload


class TestGroupMembershipModel(OGDSTestCase):

    def _load_group_with_memberships(self, group):
        return (
            self.session.query(Group)
            .options(
                selectinload(Group.memberships)
                .selectinload(GroupMembership.user)
            )
            .filter_by(groupid=group.groupid)
            .one()
        )

    def _load_user_with_memberships(self, user):
        return (
            self.session.query(User)
            .options(
                selectinload(User.memberships)
                .selectinload(GroupMembership.group)
            )
            .filter_by(userid=user.userid)
            .one()
        )

    def test_create_membership_with_optional_note(self):
        self.member_b = self._load_group_with_memberships(self.members_b)
        self.assertNotIn(self.john, self.member_b.users)
        self.assertEqual(2, len(self.member_b.memberships))

        member_john = GroupMembership(
            groupid=self.members_b.groupid, userid=self.john.userid, note="Test Note"
        )

        self.session.add(member_john)
        self.session.flush()
        self.session.expire(self.members_b, ['memberships', 'users'])
        self.member_b = self._load_group_with_memberships(self.members_b)
        self.session.expire(self.john, ["groups"])

        self.assertEqual(3, len(self.member_b.memberships))
        self.assertEqual("Test Note", member_john.note)

        self.assertIn(self.john, self.members_b.users)
        self.assertIn(self.members_b, self.john.groups)

    def test_delete_orphan_cascades_when_removed_from_collection(self):
        m1 = GroupMembership(groupid=self.members_a.groupid, userid=self.jack.userid)
        m2 = GroupMembership(groupid=self.members_b.groupid, userid=self.jack.userid)
        self.session.add_all([m1, m2])
        self.session.flush()

        self.members_a = self._load_group_with_memberships(self.members_a)
        self.members_a.memberships.remove(m1)
        self.session.flush()

        self.assertNotIn(
            self.members_a.groupid, [m.groupid for m in self.jack.memberships]
        )
        self.assertNotIn(
            self.jack.userid, [m.userid for m in self.members_a.memberships]
        )
        self.assertNotIn(self.members_a, self.jack.groups)
        self.assertNotIn(self.jack, self.members_a.users)

    def test_delete_orphan_on_user_side(self):
        member_peter = (
            self.session.query(GroupMembership)
            .filter_by(groupid=self.members_b.groupid, userid=self.peter.userid)
            .one()
        )

        self.peter = self._load_user_with_memberships(self.peter)
        self.peter.memberships.remove(member_peter)
        self.session.flush()
        self.session.expire(self.members_b, ["memberships", "users"])
        self.session.expire(self.peter, ["groups"])

        self.assertNotIn(
            self.members_b.groupid, [m.groupid for m in self.peter.memberships]
        )
        self.assertNotIn(self.peter, self.members_b.users)
        self.assertNotIn(self.members_b, self.peter.groups)
