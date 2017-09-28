from ftw.builder import Builder
from ftw.builder import create
from opengever.contact.models import Contact
from opengever.testing import MEMORY_DB_LAYER
import unittest


class TestPolymorphicQuery(unittest.TestCase):

    layer = MEMORY_DB_LAYER

    def test_returns_organizations(self):
        meier_ag = create(Builder('organization').named(u'Meier AG'))
        create(Builder('organization').named(u'Other AG'))

        query = Contact.query.polymorphic_by_searchable_text(
            text_filters=['Meier*'])
        self.assertEqual([meier_ag], query.all())

    def test_returns_persons(self):
        peter = create(
            Builder('person').having(firstname=u'Peter',
                                     lastname=u'M\xfcller'))
        create(Builder('person')
               .having(firstname=u'Hans', lastname=u'M\xfcller'))

        query = Contact.query.polymorphic_by_searchable_text(
            text_filters=['Pete*'])
        self.assertEqual([peter], query.all())

    def test_returns_both_entities(self):
        peter = create(
            Builder('person').having(firstname=u'Peter',
                                     lastname=u'M\xfcller'))
        create(Builder('person')
               .having(firstname=u'Hans', lastname=u'M\xfcller'))

        peter_co = create(Builder('organization').named(u'Peter & Co.'))
        create(Builder('organization').named(u'Meier AG'))

        query = Contact.query.polymorphic_by_searchable_text(
            text_filters=['Pete*'])
        self.assertEqual([peter, peter_co], query.all())

    def test_returns_org_roles_with_matching_function_for_one_entity(self):
        ftw = create(Builder('organization').named(u'4teamwork AG'))
        meier_ag = create(Builder('organization').named(u'Meier AG'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))

        role1 = create(Builder('org_role')
                       .having(person=peter,
                               organization=meier_ag,
                               function='Developer'))

        create(Builder('org_role')
               .having(person=peter, organization=ftw, function='Member'))

        query = Contact.query.polymorphic_by_searchable_text(
            text_filters=['Develop*'])

        results = query.all()
        self.assertEqual([peter], results)
        self.assertEqual([role1], results[0].organizations)

    def test_returns_org_roles_with_matching_function_for_multiple_entities(self):
        ftw = create(Builder('organization').named(u'4teamwork AG'))
        meier_ag = create(Builder('organization').named(u'Meier AG'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        hans = create(Builder('person')
                      .having(firstname=u'Hans', lastname=u'M\xfcller'))

        role1 = create(Builder('org_role')
                       .having(person=peter,
                               organization=meier_ag,
                               function='Developer'))

        create(Builder('org_role')
               .having(person=peter, organization=ftw, function='Member'))

        role3 = create(Builder('org_role')
                       .having(person=hans,
                               organization=meier_ag,
                               function='Developer'))

        create(Builder('org_role')
               .having(person=hans, organization=ftw,))

        query = Contact.query.polymorphic_by_searchable_text(
            text_filters=['Develop*'])

        results = query.all()
        self.assertEqual([peter, hans], results)
        self.assertEqual([role1], results[0].organizations)
        self.assertEqual([role3], results[1].organizations)
