from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestOrganizationalRole(unittest.TestCase):

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

    def test_organization_title_is_person_organization_and_suffix_in_parentheses(self):
        peter = create(Builder('person')
                       .having(firstname=u'Peter',
                               lastname=u'M\xfcller',
                               former_contact_id=123456))

        teamwork = create(Builder('organization').named(u'4teamwork AG'))
        meier = create(Builder('organization').named(u'Meier AG'))

        role1 = create(Builder('org_role').having(person=peter,
                                                  organization=meier))

        role2 = create(Builder('org_role').having(person=peter,
                                                  organization=teamwork,
                                                  function='Developer'))

        role3 = create(Builder('org_role').having(person=peter,
                                                  organization=teamwork,
                                                  function='Developer',
                                                  department='IT'))

        role4 = create(Builder('org_role').having(person=peter,
                                                  organization=teamwork,
                                                  department='IT'))

        self.assertEquals(
            u'M\xfcller Peter - Meier AG', role1.get_title())
        self.assertEquals(
            u'M\xfcller Peter - 4teamwork AG (Developer)', role2.get_title())
        self.assertEquals(
            u'M\xfcller Peter - 4teamwork AG (Developer - IT)', role3.get_title())
        self.assertEquals(
            u'M\xfcller Peter - 4teamwork AG (IT)', role4.get_title())

        self.assertEquals(
            u'M\xfcller Peter [123456] - Meier AG',
            role1.get_title(with_former_id=True))
