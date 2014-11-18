from AccessControl import Unauthorized
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import create_plone_user
from opengever.testing import FunctionalTestCase
from opengever.trash.remover import Remover
from plone import api
from plone.app.testing import setRoles
import transaction


class TestRemover(FunctionalTestCase):

    def setUp(self):
        super(TestRemover, self).setUp()
        self.grant('Administrator')

    def test_changes_state_to_removed_for_all_documents(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document').trashed())

        Remover([doc1, doc2]).remove()

        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=doc1))
        self.assertEquals('document-state-removed',
                          api.content.get_state(obj=doc2))

    def test_raises_runtimeerror_when_preconditions_are_not_satisified(self):
        doc1 = create(Builder('document').trashed())
        doc2 = create(Builder('document'))

        with self.assertRaises(RuntimeError) as cm:
            Remover([doc1, doc2]).remove()

        self.assertEquals('RemoveConditions not satisified',
                          str(cm.exception))

    def test_raises_unauthorized_when_user_has_not_remove_permission(self):
        doc1 = create(Builder('document').trashed())

        create_plone_user(self.portal, 'hugo.boss')
        self.login(user_id='hugo.boss')
        setRoles(self.portal, 'hugo.boss', ['Member'])
        transaction.commit()

        with self.assertRaises(Unauthorized):
            Remover([doc1]).remove()
