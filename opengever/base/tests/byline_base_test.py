from opengever.testing import FunctionalTestCase
from ftw.testbrowser import browser as default_browser


class TestBylineBase(FunctionalTestCase):

    def get_byline_value_by_label(self, label, browser=default_browser):
        byline_elements = browser.css(".documentByLine li")

        for element in byline_elements:
            if element.css('.label').first.text == label:
                return element.css('> *')[1]
