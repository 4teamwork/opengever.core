from opengever.testing import Builder
from opengever.testing import FunctionalTestCase


class TestMoveItems(FunctionalTestCase):

    def setUp(self):
        super(TestMoveItems, self).setUp()
        self.grant('Contributor')
        self.request = self.layer['request']

        self.source_repo = Builder("repository").create()
        self.source_dossier = Builder("dossier") \
            .within(self.source_repo).create()

    def test_cant_move_items_to_invalid_target(self):
        bad_target = Builder("repository").create()
        task1 = Builder("task") \
            .within(self.source_dossier).titled("a Task").create()

        self.assert_contains(self.source_dossier, ['a Task'])
        self.assert_contains(bad_target, [])

        self.move_items([task1], source=self.source_dossier, target=bad_target)

        self.assert_contains(self.source_dossier, ['a Task'])
        self.assert_contains(bad_target, [])

    def test_render_documents_tab_when_no_items_are_selected(self):
        view = self.source_dossier.restrictedTraverse('move_items')

        self.assertEquals("%s#documents" % self.source_dossier.absolute_url(), view())

    def test_render_orig_template_when_no_items_are_selected(self):
        view = self.source_dossier.restrictedTraverse('move_items')
        self.request.form['orig_template'] = "%s#dossiers" % self.source_dossier.absolute_url()
        self.assertEquals("%s#dossiers" % self.source_dossier.absolute_url(), view())

    def test_move_items_to_valid_target(self):
        """ Test integration of move_items method
        """

        target_repo = Builder("repository").create()

        target_dossier = Builder("dossier").within(target_repo).create()

        doc1 = Builder("document") \
            .within(self.source_dossier).titled(u"Dossier \xb6c1").create()
        task1 = Builder("task") \
            .within(self.source_dossier).titled("a Task").create()
        subdossier1 = Builder("dossier") \
            .within(self.source_dossier).titled("a Dossier").create()

        self.assert_contains(self.source_dossier,
                             ['Dossier \xc2\xb6c1', 'a Task', 'a Dossier'])
        self.assert_contains(target_dossier, [])

        self.move_items([doc1, task1, subdossier1],
                        source=self.source_dossier,
                        target=target_dossier)

        self.assert_contains(self.source_dossier, [])
        self.assert_contains(target_dossier,
                             ['Dossier \xc2\xb6c1', 'a Task', 'a Dossier'])

    def move_items(self, items, source=None, target=None):
        paths = u";;".join(["/".join(i.getPhysicalPath()) for i in items])
        self.request['paths'] = paths
        self.request['form.widgets.request_paths'] = paths
        self.request['form.widgets.destination_folder'] = "/".join(
            target.getPhysicalPath())

        view = source.restrictedTraverse('move_items')
        form = view.form(source, self.request)
        form.updateWidgets()
        form.widgets['destination_folder'].value = target
        form.widgets['request_paths'].value = paths

        form.handle_submit(form, object)

    def assert_contains(self, container, items):
        self.assertEquals(items,
                          [a.Title for a in container.getFolderContents()])
