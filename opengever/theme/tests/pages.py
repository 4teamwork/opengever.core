from ftw.testing import browser
from ftw.testing.pages import Plone


class SearchBox(Plone):

    @property
    def search_field_placeholder(self):
        xpr = '#portal-searchbox input[name=SearchableText]'
        return browser().find_by_css(xpr).first['placeholder']
