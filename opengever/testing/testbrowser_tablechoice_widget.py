from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class TableChoiceWidget(PloneWidget):
    """Fill the table choice widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css('.tableradio-widget-wrapper')) > 0

    def fill(self, value):
        input = self.input_by_option.get(value)
        if not input:
            raise ValueError('No such option {!r}. Options: {!r}'.format(
                value, self.options))
        input.checked = True

    @property
    def wrapper(self):
        return self.css('.tableradio-widget-wrapper').first

    @property
    def options(self):
        return self.input_by_option.keys()

    @property
    def table(self):
        return self.css('.listing').first

    @property
    def input_by_option(self):
        options = {}
        for input in self.wrapper.css('td:first-child input'):
            options[input.attrib['value']] = input
            title = input.attrib.get('title')
            if title:
                options[title] = input

        return options
