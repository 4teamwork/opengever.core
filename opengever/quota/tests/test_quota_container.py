from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from opengever.core.testing import OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER
from opengever.private.interfaces import IPrivateFolderQuotaSettings
from opengever.private.tests import create_members_folder
from opengever.quota.interfaces import HARD_LIMIT_EXCEEDED
from opengever.quota.interfaces import SOFT_LIMIT_EXCEEDED
from opengever.quota.sizequota import ISizeQuota
from opengever.testing import FunctionalTestCase
from opengever.trash.trash import ITrashable
from plone.namedfile.file import NamedBlobFile
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class TestSizeQuota(FunctionalTestCase):
    layer = OPENGEVER_FUNCTIONAL_PRIVATE_FOLDER_LAYER

    def test_content_modifications_update_usage(self):
        """Test that adding, updating, removing and moving update the usage.

        This test is implemented as story so that we do not create that many
        objects in order to speed up tests.
        As soon as we can use fixtures these tests can be refactored.
        """
        self.grant('Manager')

        user_folder = create_members_folder(create(Builder('private_root')))
        user_dossier = create(Builder('dossier').within(user_folder))
        shared_dossier = create(Builder('dossier'))
        self.assertEqual(0, ISizeQuota(user_folder).get_usage(),
                         'Expected usage to be 0 for an empty root.')

        with self.assert_usage_change(user_folder, +1,
                                      'add first document'):
            doc1 = create(Builder('document')
                          .attach_file_containing('X')
                          .within(user_dossier))

        with self.assert_usage_change(user_folder, -1 + 2,
                                      'update document'):
            doc1.file = NamedBlobFile('XX', filename=u'test.txt')
            notify(ObjectModifiedEvent(doc1))

        with self.assert_usage_change(user_folder, +3,
                                      'add second document'):
            doc2 = create(Builder('document')
                          .attach_file_containing('XXX')
                          .within(user_dossier))

        with self.assert_usage_change(user_folder, -3,
                                      'move away from quota container'):
            shared_dossier.manage_pasteObjects(
                user_dossier.manage_cutObjects([doc2.getId()]))

        with self.assert_usage_change(user_folder, +3,
                                      'move back into quota container'):
            user_dossier.manage_pasteObjects(
                shared_dossier.manage_cutObjects([doc2.getId()]))

        with self.assert_usage_change(user_folder, -3, 'trash document'):
            ITrashable(doc2).trash()

        with self.assert_usage_change(user_folder, +3, 'restore document'):
            ITrashable(doc2).untrash()

        with self.assert_usage_change(user_folder, -3,
                                      'delete'):
            user_dossier.manage_delObjects([doc2.getId()])

        # clear and recalculate
        self.assertEqual(2, ISizeQuota(user_folder).get_usage())
        ISizeQuota(user_folder).get_usage_map(for_writing=True).clear()
        self.assertEqual(0, ISizeQuota(user_folder).get_usage())
        ISizeQuota(user_folder).recalculate()
        self.assertEqual(2, ISizeQuota(user_folder).get_usage())

    def test_exceeded_limit(self):
        user_folder = create_members_folder(create(Builder('private_root')))
        create(Builder('document').attach_file_containing('X' * 100)
               .within(user_folder))
        quota = ISizeQuota(user_folder)
        settings = getUtility(IRegistry).forInterface(
            IPrivateFolderQuotaSettings)

        self.assertEqual(100, quota.get_usage())
        self.assertEqual(None, quota.exceeded_limit())

        settings.size_soft_limit = 70
        self.assertEqual(SOFT_LIMIT_EXCEEDED, quota.exceeded_limit())

        settings.size_hard_limit = 80
        self.assertEqual(HARD_LIMIT_EXCEEDED, quota.exceeded_limit())

        settings.size_soft_limit = 110
        settings.size_hard_limit = 120
        self.assertEqual(None, quota.exceeded_limit())

    @contextmanager
    def assert_usage_change(self, container, increase, action):
        before = ISizeQuota(container).get_usage()
        yield
        after = ISizeQuota(container).get_usage()
        self.assertEqual(
            increase, after - before,
            'Unexpected usage after: {}'.format(action))
