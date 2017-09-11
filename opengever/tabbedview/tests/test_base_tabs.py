from opengever.testing import IntegrationTestCase
from ftw.testbrowser import browsing
from plone import api
from opengever.base.interfaces import IReferenceNumberSettings


class TestGeverTabMixin(IntegrationTestCase):

    @browsing
    def test_reference_number_custom_sort(self, browser):
        self.login(self.regular_user)

        api.portal.set_registry_record(
            name='formatter',
            value='grouped_by_three',
            interface=IReferenceNumberSettings)

        listing_view = self.leaf_repofolder.restrictedTraverse(
            'tabbedview_view-dossiers')

        results = listing_view.custom_sort(
            ['OG 921.11-2', 'OG 921.11-1', 'OG 921.11-12', 'OG 921.11-11'],
            sort_on='reference', sort_reverse=False)

        self.assertEquals(
            ['OG 921.11-1', 'OG 921.11-2', 'OG 921.11-11', 'OG 921.11-12'],
            results)
