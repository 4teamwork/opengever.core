from ftw.builder import builder_registry
from ftw.builder.portlets import PlonePortletBuilder
from opengever.portlets.tree import treeportlet


class TreePortletBuilder(PlonePortletBuilder):
    assignment_class = treeportlet.Assignment

    def for_root(self, repository_root):
        self.having(root_path=repository_root.getId())
        return self


builder_registry.register('tree portlet', TreePortletBuilder)
