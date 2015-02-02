from ftw.testbrowser.widgets.autocomplete import AutocompleteWidget
from ftw.testbrowser.widgets.base import widget


@widget
class OpengeverAutocompleteWidget(AutocompleteWidget):
    """Represents the autocomplete widget that has been customized for OpenGever.
    """

    def query(self, query_string):
        """Customized for the OpenGever specific autocomplete widget:

        Uses `term` parameter instead of `q` to pass the search query, and
        deals with unpacking the different response format.
        """
        url = self._get_query_url()

        with self.browser.clone() as query_browser:
            query_browser.open(url, data={'term': query_string})
            return [[item.get('value'), item.get('label')]
                    for item in query_browser.json]
