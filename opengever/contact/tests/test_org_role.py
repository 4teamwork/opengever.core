from opengever.contact.models import Organisation
from opengever.contact.models import OrgRole
from opengever.contact.models import Person
from opengever.testing import MEMORY_DB_LAYER
import unittest2


class TestOrganisationalRole(unittest2.TestCase):

    layer = MEMORY_DB_LAYER

    def test_organisation_person_relation(self):
        school = Organisation(name='4teamwork AG')
        meier_ag = Organisation(name='Meier AG')

        peter = Person(firstname=u'Peter', lastname=u'M\xfcller')
        hugo = Person(firstname=u'Hugo', lastname=u'Boss')

        role1 = OrgRole(person=peter, organisation=meier_ag,
                         function='Developer')
        role2 = OrgRole(person=hugo, organisation=meier_ag, function='CTO')
        role3 = OrgRole(person=peter, organisation=school, function='Member')

        self.assertEquals([role1, role3], peter.organisations)
        self.assertEquals([role2], hugo.organisations)
        self.assertEquals([peter, hugo],
                          [role.person for role in meier_ag.persons])
