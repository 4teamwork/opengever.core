from ftw.upgrade import UpgradeStep
from plone import api


class RemoveImportStep(UpgradeStep):

    def __call__(self):
        setup = api.portal.get_tool('portal_setup')
        reg = setup.getImportStepRegistry()
        reg.unregisterStep('opengever_tabbedview_configuration')
