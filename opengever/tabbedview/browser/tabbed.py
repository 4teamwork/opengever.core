from ftw.tabbedview.browser.tabbed import TabbedView


class GeverTabbedView(TabbedView):
    """Customized tabbedview that adds support for tab-definitions without
    defining actions in the fti of a type.

    To do so define a method `_get_tabs` that returns a list of dicts that
    contain at least the keys `id` and `title`. E.g.:

    ```
    def _get_tabs(self):
        return [
            {'id': 'overview',
             'title': _(u'overview', default=u'Overview')}
        ]
    ```

    They keys `icon`, `url` and `class` are also required by ftw.tabbedview,
    but usually left empty. Thus a default value will be filled in for your
    convenience.
    """

    def _make_tab_with_defaults(self):

        return {
            'icon': None,
            'url': '#',
            'class': None
        }

    def _fill_with_defaults(self, tabs):
        finished_tabs = []
        for tab in tabs:
            if tab is None:
                continue
            new_tab = self._make_tab_with_defaults()
            # overwrite defaults with definition, if specified
            new_tab.update(tab)
            finished_tabs.append(new_tab)
        return finished_tabs

    def get_tabs(self):
        if hasattr(self, '_get_tabs'):
            return self._fill_with_defaults(self._get_tabs())

        return super(GeverTabbedView, self).get_tabs()


class ModelProxyTabbedView(GeverTabbedView):
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
