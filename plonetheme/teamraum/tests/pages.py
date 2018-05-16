from ftw.testbrowser import browser as default_browser


def search_field_placeholder(browser=default_browser):
    """Returns the placeholder text of the Plone search box.
    """
    xpr = '#portal-searchbox input[name=SearchableText]'
    return browser.css(xpr).first.attrib['placeholder']
