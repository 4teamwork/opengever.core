from opengever.testing import FunctionalTestCase


class TestBylineBase(FunctionalTestCase):
    use_browser = True

    def get_byline_value_by_label(self, label):
        byline_elements = self.browser.css(".documentByLine li")

        for element in byline_elements:
            for element_label in element.target.cssselect('.label'):
                if element_label.text_content().strip() == label:
                    return element.target.getchildren()[1]

    def get_byline_element_by_class(self, css_class):
        byline_elements = self.browser.css(".documentByLine li")
        for element in byline_elements:
            if element.get('class') and css_class in element.get('class').split():
                return element
