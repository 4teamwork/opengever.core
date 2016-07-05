from opengever.contact.models import Organization
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganizationalRole(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_organization_person_relation(self):
        school = Organization(name='4teamwork AG')
        meier_ag = Organization(name='Meier AG')

        peter = Person(firstname=u'Peter', lastname=u'M\xfcller')
        hugo = Person(firstname=u'Hugo', lastname=u'Boss')

        role1 = OrgRole(person=peter, organization=meier_ag,
                         function='Developer')
        role2 = OrgRole(person=hugo, organization=meier_ag, function='CTO')
        role3 = OrgRole(person=peter, organization=school, function='Member')

        self.assertEquals([role1, role3], peter.organizations)
        self.assertEquals([role2], hugo.organizations)
        self.assertEquals([peter, hugo],
                          [role.person for role in meier_ag.persons])
