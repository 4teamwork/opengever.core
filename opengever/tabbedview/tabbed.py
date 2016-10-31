from ftw.tabbedview.browser.tabbed import TabbedView


class ModelProxyTabbedView(TabbedView):
    """Prepare which **ContentView** tabs are visible on the default view
    of a model proxy.

    """
    is_model_proxy_view = True

    def prepare_model_proxy_tabs(self, contentview_tabs):
        visible_tabs = []
        for contentview_tab in contentview_tabs:
            if self.is_visible(contentview_tab):
                visible_tabs.append(contentview_tab)
        return visible_tabs

    def is_visible(self, contentview_tab):
        if contentview_tab.get('id') == 'edit':
            return self.context.is_editable()
        return True
