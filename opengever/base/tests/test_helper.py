from ftw.testing import MockTestCase
from opengever.base.browser.helper import get_css_class
from opengever.globalindex.model.task import Task as GlobalindexTask
from opengever.ogds.base import utils
from plone.i18n.normalizer import idnormalizer, IIDNormalizer


class TestCssClassHelpers(MockTestCase):

    def setUp(self):
        super(TestCssClassHelpers, self).setUp()

        self.ori_get_current_admin_unit = utils.get_current_admin_unit
        get_current_admin_unit = self.mocker.replace(
            'opengever.ogds.base.utils.get_current_admin_unit', count=False)

        admin_unit = self.stub()
        self.expect(get_current_admin_unit()).result(admin_unit)
        self.expect(admin_unit.id()).result('client1')

        self.mock_utility(idnormalizer, IIDNormalizer)

    def tearDown(self):
        utils.get_current_admin_unit = self.ori_get_current_admin_unit

    def test_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('ftw.obj.obj')

        self.replay()

        self.assertEquals(get_css_class(obj), 'contenttype-ftw-obj-obj')

    def test_forwarding(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.inbox.forwarding')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-inbox-forwarding')

    def test_forwarding_globalindex(self):
        obj = GlobalindexTask(1232, 'client1')
        obj.task_type = 'forwarding_task_type'
        obj.is_subtask = False
        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-inbox-forwarding')

    def test_document_brain_with_icon(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.document.document')
        self.expect(getattr(brain, '_v__is_relation', False)).result(False)
        self.expect(brain.getIcon).result('icon_dokument_pdf.gif')

        self.replay()

        self.assertEquals(get_css_class(brain), 'icon-dokument_pdf')

    def test_document_obj_with_icon(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.document.document')
        self.expect(getattr(obj, '_v__is_relation', False)).result(False)
        self.expect(obj.getIcon()).result('icon_dokument_word.gif')

        self.replay()

        self.assertEquals(get_css_class(obj), 'icon-dokument_word')

    def test_document_obj_with_relation_flag(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.document.document')
        self.expect(getattr(obj, '_v__is_relation', False)).result(True)
        obj._v__is_relation = False

        self.replay()

        self.assertEquals(get_css_class(obj), 'icon-dokument_verweis')

    def test_task_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.predecessor).result(None)
        self.expect(brain.is_subtask).result(False)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client1')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'contenttype-opengever-task-task')

    def test_task_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.predecessor).result(None)
        self.expect(obj.responsible_client).result('client1')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is dossier -> obj is not subtask
        self.expect(parent.portal_type).result('opengever-dossier')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-task-task')

    def test_task_globalindex(self):
        obj = GlobalindexTask(1231, 'client1')
        obj.assigned_org_unit = 'client1'
        obj.is_subtask = False
        self.replay()

        self.assertEquals(get_css_class(obj),
                          'contenttype-opengever-task-task')

    def test_subtask_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.predecessor).result(None)
        self.expect(brain.is_subtask).result(True)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client1')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'icon-task-subtask')

    def test_subtask_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.predecessor).result('client2:12345')
        self.expect(obj.responsible_client).result('client1')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is task -> obj is subtask
        self.expect(parent.portal_type).result('opengever.task.task')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-subtask')

    def test_subtask_globalindex(self):
        obj = GlobalindexTask(1231, 'client1')
        obj.assigned_org_unit = 'client1'
        obj.is_subtask = True
        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-subtask')

    def test_remote_task_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.predecessor).result('client2:12345')
        self.expect(brain.is_subtask).result(False)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client2')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'icon-task-remote-task')

    def test_remote_task_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.predecessor).result('client2:12345')
        self.expect(obj.responsible_client).result('client2')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is dossier -> obj is not subtask
        self.expect(parent.portal_type).result('opengever-dossier')

        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-remote-task')

    def test_remote_task_globalindex(self):
        obj = GlobalindexTask(1231, 'client1')
        obj.assigned_org_unit = 'client2'
        obj.is_subtask = False
        self.replay()

        self.assertEquals(get_css_class(obj),
                          'icon-task-remote-task')

    def test_remote_successor_task_brain(self):
        brain = self.stub()
        self.expect(brain.portal_type).result('opengever.task.task')
        self.expect(brain.is_subtask).result(False)
        self.expect(brain.client_id).result('client1')
        self.expect(brain.assigned_client).result('client1')
        self.expect(brain.predecessor).result('client2:12345')

        self.replay()

        self.assertEquals(get_css_class(brain),
                          'icon-task-remote-task')

    def test_remote_successor_task_obj(self):
        obj = self.stub()
        self.expect(obj.portal_type).result('opengever.task.task')
        self.expect(obj.responsible_client).result('client1')
        self.expect(obj.predecessor).result('client2:123456')

        parent = self.stub()
        self.set_parent(obj, parent)
        # parent is dossier -> obj is not subtask
        self.expect(parent.portal_type).result('opengever-dossier')

        self.replay()

        self.assertEquals('icon-task-remote-task', get_css_class(obj))

    def test_remote_successor_task_globalindex(self):
        obj = GlobalindexTask(1231, 'client1')
        obj.assigned_org_unit = 'client1'
        obj.predecessor = GlobalindexTask(11111, 'client2')
        obj.is_subtask = False
        self.replay()

        self.assertEquals('icon-task-remote-task', get_css_class(obj))

    def test_remote_subtask_globalindex__issuer(self):
        # Tests task which is both, remote and subtask, from the
        # perspective of the issuer (on issuers client).
        obj = GlobalindexTask(1231, 'client1')
        obj.assigned_org_unit = 'client2'
        obj.is_subtask = True
        # current-client: client1
        self.replay()

        self.assertEquals('icon-task-subtask', get_css_class(obj), )

    def test_remote_subtask_globalindex__responsible(self):
        # Tests task which is both, remote and subtask, from the
        # perspective of the responsible (on responsible's client).
        obj = GlobalindexTask(1231, 'client2')
        obj.assigned_org_unit = 'client1'
        obj.is_subtask = True
        # current-client: client1
        self.replay()

        self.assertEquals('icon-task-remote-task', get_css_class(obj))
