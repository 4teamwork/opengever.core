from lxml.cssselect import CSSSelector
from plone.testing.z2 import Browser

import lxml.html

class OGHtmlElementWrapper(object):

    def __init__(self, target):
        self.target = target

    def plain_text(self):
        if self.text:
            return self.text_content().strip()
        else:
            None

    def __getattr__(self, name):
        return getattr(self.target, name)

class OGBrowser(Browser):

    def fill(self, data):
        for selector,value in data.items():
            self.fill_in(selector, value)

    def fill_in(self, selector, value):
        self.control(selector).value = value

    def check(self, selector):
        self.control(selector).selected = True

    def click(self, selector):
        self.control(selector).click()

    def control(self, selector):
        try:
            return self.getControl(selector)
        except LookupError:
            return self.getControl(name=selector)

    def locate(self, css_selector):
        elements = self.css(css_selector)
        if elements:
            return elements[0]
        raise AssertionError('Element for CSS selector "{}" could not be '
                             'found on the current browser '
                             'page.'.format(css_selector))

    def css(self, selector):
        xpath = CSSSelector(selector).path
        return self.xpath(xpath)

    def xpath(self, selector):
        html = lxml.html.fromstring(self.contents)
        return [OGHtmlElementWrapper(e) for e in html.xpath(selector)]

    def assert_url(self, expected_url):
        if expected_url != self.url:
            raise AssertionError("Expected %s to be %s" % (self.url, expected_url))
