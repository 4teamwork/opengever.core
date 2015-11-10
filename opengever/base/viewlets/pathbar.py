from opengever.ogds.base.utils import get_current_admin_unit
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PathBar(common.PathBarViewlet):
    index = ViewPageTemplateFile('pathbar.pt')

    def admin_unit_label(self):
        return get_current_admin_unit().label()

    def update(self):
        super(PathBar, self).update()

        if getattr(self.view, 'has_model_breadcrumbs', False):
            self.append_model_breadcrumbs()

    def append_model_breadcrumbs(self):
        model_breadcrumbs = self.view.context.get_breadcrumbs()
        self.breadcrumbs = self.breadcrumbs + model_breadcrumbs
