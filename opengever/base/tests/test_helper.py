from opengever.base.browser.helper import get_css_class
from opengever.testing import IntegrationTestCase
from opengever.testing.helpers import obj2brain


class TestCssClassHelpers(IntegrationTestCase):

    def test_document_obj_with_relation_flag(self):
        self.login(self.dossier_responsible)
        setattr(self.document, '_v__is_relation', True)
        self.assertEquals(
            get_css_class(self.document),
            'icon-docx is-document-relation')

    def test_document_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.document)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_document_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.document, '_v__is_relation', False)
        self.assertEquals(self.document.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.document), 'icon-docx')

    def test_sablontemplate_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.sablon_template)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_sablontemplate_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.sablon_template, '_v__is_relation', False)
        self.assertEquals(self.sablon_template.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.sablon_template), 'icon-docx')

    def test_proposaltemplate_brain_with_icon(self):
        self.login(self.dossier_responsible)
        brain = obj2brain(self.proposal_template)
        self.assertEquals(brain.getIcon, 'docx.png')
        self.assertEquals(get_css_class(brain), 'icon-docx')

    def test_proposaltemplate_obj_with_icon(self):
        self.login(self.dossier_responsible)
        setattr(self.proposal_template, '_v__is_relation', False)
        self.assertEquals(self.proposal_template.getIcon(), 'docx.png')
        self.assertEquals(get_css_class(self.proposal_template), 'icon-docx')

    def test_task_obj(self):
        self.login(self.dossier_responsible)
        self.assertEquals('contenttype-opengever-task-task',
                          get_css_class(self.task))

    def test_document_obj_checked_out_suffix(self):
        self.login(self.dossier_responsible)

        self.assertEquals('icon-docx', get_css_class(self.document))

        self.checkout_document(self.document)
        self.assertEquals('icon-docx is-checked-out-by-current-user',
                          get_css_class(self.document))

    def test_document_obj_checked_out_in_context_of_another_users_id(self):
        self.login(self.dossier_responsible)

        self.assertEquals('icon-docx', get_css_class(self.document))

        self.checkout_document(self.document)
        self.assertEquals(
            'icon-docx is-checked-out-by-current-user',
            get_css_class(self.document, for_user=self.dossier_responsible.id))

        self.assertEquals(
            'icon-docx is-checked-out',
            get_css_class(self.document, for_user=self.regular_user.id))

    def test_document_brain_checked_out_suffix(self):
        self.login(self.dossier_responsible)

        self.assertEquals('icon-docx', get_css_class(obj2brain(self.document)))

        self.checkout_document(self.document)
        self.assertEquals('icon-docx is-checked-out-by-current-user',
                          get_css_class(obj2brain(self.document)))

    def test_proposaltemplate_checked_out_suffix(self):
        self.login(self.dossier_responsible)

        self.assertEquals('icon-docx', get_css_class(self.proposal_template))

        self.checkout_document(self.proposal_template)
        self.assertEquals('icon-docx is-checked-out-by-current-user',
                          get_css_class(obj2brain(self.proposal_template)))

    def test_document_obj_checked_out_by_other_suffix(self):
        self.login(self.dossier_responsible)
        self.checkout_document(self.document)

        self.login(self.regular_user)
        self.assertEquals('icon-docx is-checked-out',
                          get_css_class(self.document))

    def test_document_brain_checked_out_by_other_suffix(self):
        self.login(self.dossier_responsible)
        self.checkout_document(self.document)

        self.login(self.regular_user)
        self.assertEquals('icon-docx is-checked-out',
                          get_css_class(obj2brain(self.document)))

    def test_proposaltemplate_checked_out_by_other_suffix(self):
        self.login(self.dossier_responsible)
        self.checkout_document(self.proposal_template)

        self.login(self.regular_user)
        self.assertEquals('icon-docx is-checked-out',
                          get_css_class(obj2brain(self.proposal_template)))
