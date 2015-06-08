from opengever.setup.hooks import assign_default_navigation_portlet


def default_content_installed(site):
    assign_default_navigation_portlet(site, 'eingangskorb')
    assign_default_navigation_portlet(site, 'vorlagen')
    assign_default_navigation_portlet(site, 'kontakte')
