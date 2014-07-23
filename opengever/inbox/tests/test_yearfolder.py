from datetime import date
from ftw.builder import Builder
from ftw.builder import create
from opengever.task.browser.accept.utils import get_current_yearfolder
from opengever.testing import FunctionalTestCase


class TestYearFolderGetter(FunctionalTestCase):

    def setUp(self):
        super(TestYearFolderGetter, self).setUp()

        create(Builder('fixture').with_all_unit_setup())

        self.main_inbox = create(Builder('inbox'))
        self.client1_inbox = create(Builder('inbox')
                                    .within(self.main_inbox)
                                    .having(responsible_org_unit='client1'))
        self.client2_inbox = create(Builder('inbox')
                                    .within(self.main_inbox)
                                    .having(responsible_org_unit='client2'))

        self.current_year = unicode(date.today().year)

    def test_returns_yearfolder_of_the_current_year(self):
        yearfolder = create(Builder('yearfolder')
                            .within(self.main_inbox)
                            .having(id=self.current_year))

        self.assertEquals(self.current_year, yearfolder.getId())
        self.assertEquals(yearfolder,
                          get_current_yearfolder(inbox=self.main_inbox))

    def test_creates_yearfolder_of_the_current_year_when_not_exists(self):
        yearfolder = get_current_yearfolder(inbox=self.main_inbox)

        self.assertEquals(self.current_year, yearfolder.getId())
        self.assertEquals('Closed {}'.format(self.current_year),
                          yearfolder.Title())

    def test_observe_current_inbox_when_context_is_given(self):
        client1_yearfolder = create(Builder('yearfolder')
                                    .within(self.client1_inbox)
                                    .having(id=self.current_year))

        create(Builder('yearfolder')
               .within(self.client2_inbox)
               .having(id=self.current_year))

        self.assertEquals(client1_yearfolder,
                          get_current_yearfolder(context=self.portal))

    def test_raises_when_both_context_and_inbox_are_missing(self):
        with self.assertRaises(ValueError) as cm:
            get_current_yearfolder()

        self.assertEquals(
            'Context or the current inbox itself must be given.',
            str(cm.exception))
