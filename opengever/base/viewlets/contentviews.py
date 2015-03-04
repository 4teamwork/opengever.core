from plone.app.layout.viewlets.common import ContentViewsViewlet


class ModelContentViewsViewlet(ContentViewsViewlet):
    """Provide correct edit links for a SQL-model based view.

    For plone content fall-back to default content views.
    """

    def prepareObjectTabs(self, default_tab='view', sort_first=('folderContents',)):
        """Prepare the object tabs by determining their order and working
        out which tab is selected. Used in global_contentviews.pt
        """

        if getattr(self.view, 'is_model_view', False):
            return self.prepare_model_tabs()
        else:
            tabs = super(ModelContentViewsViewlet, self).prepareObjectTabs(
                default_tab, sort_first)
            if getattr(self.view, 'is_model_proxy_view', False):
                tabs = self.view.prepare_model_proxy_tabs(tabs)
            return tabs

    def prepare_model_tabs(self):
        model = self.view.model
        return ({
            'category': 'object',
            'available': True,
            'description': u'',
            'icon': '',
            'title': u'Edit',
            'url': model.get_edit_url(self.view.context),
            'selected': self.view.is_model_edit_view,
            'visible': True,
            'allowed': True,
            'link_target': None,
            'id': 'edit'
        },)
