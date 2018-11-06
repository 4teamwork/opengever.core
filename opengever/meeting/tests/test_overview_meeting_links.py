from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from operator import attrgetter


class TestDocumentOverviewMeetingLinks(IntegrationTestCase):

    features = ('meeting',)

    @browsing
    def test_overview_displays_link_to_proposal(self, browser):
        expected_fields = sorted([
            'Title',
            'Document Date',
            'Document Type',
            'Author',
            'creator',
            'Description',
            'Foreign Reference',
            'Keywords',
            'Checked out',
            'File',
            'Digital Available',
            'Preserved as paper',
            'Date of receipt',
            'Date of delivery',
            'Related Documents',
            'Classification',
            'Privacy layer',
            'Public Trial',
            'Public trial statement',
            'Submitted with',
            'Proposal',
            'Created',
            'Modified',
        ])

        self.login(self.secretariat_user, browser)
        browser.open(self.proposal.get_proposal_document(),
                     view='tabbedview_view-overview')
        fields = dict(zip(
            browser.css('.documentMetadata th').text,
            map(attrgetter('innerHTML'), browser.css('.documentMetadata td')),
        ))

        self.assertEquals(expected_fields,
                          sorted(fields.keys()))
        self.assertEquals(
            u'<a href="http://nohost/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1/proposal-1" '
            u'title="Vertr\xe4ge" class="contenttype-opengever-meeting-proposal">Vertr\xe4ge</a>',
            fields['Proposal']
        )

    @browsing
    def test_overview_displays_link_to_meeting(self, browser):
        expected_fields = sorted([
            'Title',
            'Document Date',
            'Document Type',
            'Author',
            'creator',
            'Description',
            'Foreign Reference',
            'Keywords',
            'Checked out',
            'File',
            'Digital Available',
            'Preserved as paper',
            'Date of receipt',
            'Date of delivery',
            'Related Documents',
            'Classification',
            'Privacy layer',
            'Public Trial',
            'Public trial statement',
            'Submitted with',
            'Proposal',
            'Meeting',
            'Created',
            'Modified',
        ])
        with self.login(self.committee_responsible, browser):
            self.proposal.load_model().schedule(self.meeting.model)

            browser.open(self.proposal.get_proposal_document(),
                         view='tabbedview_view-overview')
            fields = dict(zip(
                browser.css('.documentMetadata th').text,
                map(attrgetter('innerHTML'), browser.css('.documentMetadata td')),
            ))
            self.assertEquals(expected_fields,
                              sorted(fields.keys()))
            self.assertEquals(
                u'<a href="http://nohost/plone/opengever-meeting-committeecontainer'
                u'/committee-1/meeting-1/view" title="9. Sitzung der '
                u'Rechnungspr\xfcfungskommission" class="'
                u'contenttype-opengever-meeting-meeting">9. Sitzung der '
                u'Rechnungspr\xfcfungskommission</a>',
                fields['Meeting'],
            )

        with self.login(self.secretariat_user, browser):
            browser.open(self.proposal.get_proposal_document(),
                         view='tabbedview_view-overview')
            fields = dict(zip(
                browser.css('.documentMetadata th').text,
                map(attrgetter('innerHTML'), browser.css('.documentMetadata td')),
            ))

            self.assertEquals(expected_fields,
                              sorted(fields.keys()))
            self.assertEquals(
                u'<span title="9. Sitzung der '
                u'Rechnungspr\xfcfungskommission" class="'
                u'contenttype-opengever-meeting-meeting">9. Sitzung der '
                u'Rechnungspr\xfcfungskommission</span>',
                fields['Meeting'],
            )
