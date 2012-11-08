from ftw.upgrade import UpgradeStep


class RemoveTooltipPlugin(UpgradeStep):

    def __call__(self):
        js_registry = self.getToolByName('portal_javascripts')
        js_registry.manage_removeScript(
            '++resource++opengever.tabbedview-resources/jquery.tooltip.min.js')
