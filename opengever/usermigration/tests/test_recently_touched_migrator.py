from opengever.base.touched import ObjectTouchedHandler
from opengever.base.touched import RECENTLY_TOUCHED_KEY
from opengever.testing import FunctionalTestCase
from opengever.usermigration.recently_touched import RecentlyTouchedMigrator
from zope.annotation import IAnnotations


class TestRecentlyTouchedMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestRecentlyTouchedMigrator, self).setUp()
        self.portal = self.layer['portal']

        ObjectTouchedHandler().ensure_log_initialized('HANS.MUSTER')

    def test_migrates_recently_touched(self):
        RecentlyTouchedMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        annotations = IAnnotations(self.portal)
        touched_store = annotations.get(RECENTLY_TOUCHED_KEY)

        self.assertIn('hans.muster', touched_store)
        self.assertNotIn('HANS.MUSTER', touched_store)
