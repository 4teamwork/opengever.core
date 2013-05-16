from opengever.testing import FunctionalTestCase
from opengever.advancedsearch.advanced_search import AdvancedSearchForm

class TestCorrectRef(FunctionalTestCase):

    def setUp(self):
        super(TestCorrectRef, self).setUp()
        self.form = AdvancedSearchForm({},{})

    def test_remove_redundant_og(self):
        self.assertEquals(u'OG 1.6 / 1', self.form.correct_ref('OG OG 1.6/1'))

    def test_insert_slash_when_missing(self):
        self.assertEquals(u'OG 1.6 / 1', self.form.correct_ref('1.6 1'))

    def test_prepend_og_when_missing(self):
        self.assertEquals(u'OG 1.6 / 1', self.form.correct_ref('1.6 / 1'))

    def test_makes_multiple_adjustments(self):
        self.assertEquals(u'OG 1.6 / 1', self.form.correct_ref('og1.6 1'))
