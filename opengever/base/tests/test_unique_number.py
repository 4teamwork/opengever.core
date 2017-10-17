from opengever.base.interfaces import IUniqueNumberGenerator
from opengever.base.interfaces import IUniqueNumberUtility
from opengever.testing import IntegrationTestCase
from zope.component import getAdapter
from zope.component import getUtility


class TestUniqueNumberGenerator(IntegrationTestCase):

    def test_genrator(self):
        adapter = getAdapter(self.portal, IUniqueNumberGenerator)
        self.assertEquals(
            adapter.generate('test.portal.type-2011'), 1)
        self.assertEquals(
            adapter.generate('second.test.portal.type-2012'), 1)
        self.assertEquals(
            adapter.generate('test.portal.type-2012'), 1)
        self.assertEquals(
            adapter.generate('test.portal.type-2011'), 2)
        self.assertEquals(
            adapter.generate('second.test.portal.type-2012'), 2)

    def test_utility(self):
        # utility
        utility = getUtility(IUniqueNumberUtility)

        with self.login(self.regular_user):
            # first object
            self.assertEquals(
                utility.get_number(self.branch_repofolder, year='2011'), 1)
            self.assertEquals(
                utility.get_number(self.branch_repofolder, year='2012'), 1)
            self.assertEquals(
                utility.get_number(self.branch_repofolder, year='2011'), 1)

            # second object
            self.assertEquals(
                utility.get_number(self.empty_repofolder, year='2011'), 2)
            self.assertEquals(
                utility.get_number(self.empty_repofolder, year='2012'), 2)
            self.assertEquals(
                utility.get_number(self.empty_repofolder, year='2011'), 2)
            self.assertEquals(
                utility.get_number(self.empty_repofolder, foo='2011'), 1)

            # same values doesn't made problems
            self.assertEquals(
                utility.get_number(
                    self.branch_repofolder, foo='foo', bar='bar'),
                1)
            self.assertEquals(
                utility.get_number(
                    self.empty_repofolder, foo='foo', bar='bar'),
                2)
            self.assertEquals(
                utility.get_number(
                    self.empty_repofolder, foo='foo', baz='bar'),
                1)
            self.assertEquals(
                utility.get_number(
                    self.branch_repofolder, foo='foo', baz='bar'),
                2)
            self.assertEquals(
                utility.get_number(
                    self.empty_repofolder, month=('2011', 5)),
                1)
            self.assertEquals(
                utility.get_number(
                    self.empty_repofolder, month=('2011', 5)),
                1)

            # removing should also work, but the removed number is
            # not recyclable
            utility.remove_number(self.empty_repofolder, year='2011')
            self.assertEquals(
                utility.get_number(self.empty_repofolder, year='2011'), 3)
