from ftw.upgrade import UpgradeStep


class RemoveDocuComposerActions(UpgradeStep):

    def __call__(self):
        self.actions_remove_type_action(
            'opengever.dossier.businesscasedossier',
            'document_with_docucomposer')
        self.actions_remove_type_action(
            'opengever.dossier.projectdossier',
            'document_with_docucomposer')
        self.actions_remove_type_action(
            'opengever.dossier.templatedossier',
            'document_with_docucomposer')
