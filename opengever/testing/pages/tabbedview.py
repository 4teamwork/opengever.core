from ftw.testbrowser import browser as default_browser


def tabs(browser=default_browser):
    """Return the tabbedview tab link nodes.
    """
    return browser.css('.tabbedview-tabs > ul.formTabs > li.formTab > a')
