from opengever.testing import IntegrationTestCase


class TestRisDossierAddableTypes(IntegrationTestCase):

    features = ('ris',)

    def test_ris_feature_enabled_addable_types(self):
        self.login(self.regular_user)
        self.assertItemsEqual(
            ['opengever.document.document',
             'ftw.mail.mail',
             'opengever.dossier.businesscasedossier',
             'opengever.task.task',
             'opengever.ris.proposal'],
            [fti.id for fti in self.dossier.allowedContentTypes()],
        )
