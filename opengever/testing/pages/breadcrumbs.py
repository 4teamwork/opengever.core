from ftw.testbrowser import browser as default_browser


def items(browser=default_browser):
    """Return linked breadcrumb items without link separators."""

    return browser.css('#portal-breadcrumbs a')


def text_items(browser=default_browser):
    """Return linked breadcrumb items' text."""

    return items(browser).text
