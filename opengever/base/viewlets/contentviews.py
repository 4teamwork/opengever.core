from plone.app.layout.viewlets.common import ContentViewsViewlet


class ModelContentViewsViewlet(ContentViewsViewlet):
    """Provide correct edit links for a SQL-model based view.

    For plone content fall-back to default content views.
    """

    def prepareObjectTabs(self, default_tab='view', sort_first=('folderContents',)):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """
        if hasattr(self.view, 'prepare_model_tabs'):
            return self.view.prepare_model_tabs(self)
        else:
            tabs = super(ModelContentViewsViewlet, self).prepareObjectTabs(
                default_tab, sort_first)
            if getattr(self.view, 'is_model_proxy_view', False):
                tabs = self.view.prepare_model_proxy_tabs(tabs)
            return tabs

    def prepare_edit_tab(self, url, is_selected=False):
        return ({
            'category': 'object',
            'available': True,
            'description': u'',
            'icon': '',
            'title': u'Edit',
            'url': url,
            'selected': is_selected,
            'visible': True,
            'allowed': True,
            'link_target': None,
            'id': 'edit'
        },)
