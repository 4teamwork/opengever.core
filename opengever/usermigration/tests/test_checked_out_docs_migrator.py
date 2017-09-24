from ftw.builder import Builder
from ftw.builder import create
from opengever.document.interfaces import ICheckinCheckoutManager
from opengever.testing import FunctionalTestCase
from opengever.testing import obj2brain
from opengever.usermigration.checked_out_docs import CheckedOutDocsMigrator
from plone.locking.interfaces import IRefreshableLockable
from zope.component import getMultiAdapter


class TestCheckedOutDocsMigrator(FunctionalTestCase):

    def setUp(self):
        super(TestCheckedOutDocsMigrator, self).setUp()
        self.portal = self.layer['portal']

        self.old_ogds_user = create(Builder('ogds_user')
                                    .id('HANS.MUSTER')
                                    .having(active=False))
        self.new_ogds_user = create(Builder('ogds_user')
                                    .id('hans.muster')
                                    .having(active=True))

        create(Builder('user')
               .with_userid('HANS.MUSTER')
               .with_roles('Reader', 'Editor', 'Contributor'))

        create(Builder('user')
               .with_userid('hans.muster')
               .with_roles('Reader', 'Editor', 'Contributor'))

    def test_migrates_checked_out_docs(self):
        document = create(Builder('document')
                          .checked_out_by('HANS.MUSTER'))

        CheckedOutDocsMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        manager = getMultiAdapter((document, self.portal.REQUEST),
                                  ICheckinCheckoutManager)

        self.assertEquals('hans.muster', manager.get_checked_out_by())
        self.assertEquals('hans.muster', obj2brain(document).checked_out)

    def test_migrates_webdav_locks(self):
        self.login('HANS.MUSTER')
        document = create(Builder('document')
                          .with_asset_file('text.txt')
                          .checked_out_by('HANS.MUSTER'))
        lockable = IRefreshableLockable(document)
        lockable.lock()

        CheckedOutDocsMigrator(
            self.portal, {'HANS.MUSTER': 'hans.muster'}, 'move').migrate()

        self.assertEqual('hans.muster', lockable.lock_info()[0]['creator'])
