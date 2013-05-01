from ftw.upgrade import UpgradeStep


class RenameStatefilterJS(UpgradeStep):

    def __call__(self):
        js_registry = self.getToolByName('portal_javascripts')

        js_registry.renameResource(
            '++resource++opengever.tabbedview-resources/tasklisting.js',
            '++resource++opengever.tabbedview-resources/statefilter.js')
