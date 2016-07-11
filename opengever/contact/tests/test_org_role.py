from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganizationalRole(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_organization_person_relation(self):
        school = create(Builder('organization').named(u'4teamwork AG'))
        meier_ag = create(Builder('organization').named(u'Meier AG'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        hugo = create(Builder('person')
                      .having(firstname=u'Hugo', lastname=u'Boss'))

        role1 = create(Builder('org_role')
                       .having(person=peter,
                               organization=meier_ag,
                               function='Developer'))

        role2 = create(Builder('org_role')
                       .having(person=hugo,
                               organization=meier_ag,
                               function='CTO'))

        role3 = create(Builder('org_role')
                       .having(person=peter,
                               organization=school,
                               function='Member'))

        self.assertEquals([role1, role3], peter.organizations)
        self.assertEquals([role2], hugo.organizations)
        self.assertEquals([peter, hugo],
                          [role.person for role in meier_ag.persons])
