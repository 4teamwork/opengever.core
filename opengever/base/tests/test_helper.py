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
