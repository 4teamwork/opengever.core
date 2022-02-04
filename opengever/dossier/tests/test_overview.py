from datetime import date
from DateTime import DateTime
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from lxml.etree import tostring
from opengever.base.behaviors.base import IOpenGeverBase
from opengever.contact.interfaces import IContactSettings
from opengever.core.testing import toggle_feature
from opengever.dossier.behaviors.dossier import IDossier
from opengever.dossier.behaviors.participation import IParticipationAware
from opengever.testing import solr_data_for
from opengever.testing import SolrIntegrationTestCase
from plone import api
from plone.protect import createToken
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import json


class TestOverview(SolrIntegrationTestCase):

    @property
    def tested_dossier(self):
        return self.dossier

    @property
    def tested_document(self):
        # XXX - This rotates out as we have more than 10 in the fixture
        return self.empty_document

    @property
    def tested_task(self):
        # XXX - This rotates out as we have more than 5 in the fixture
        return self.inbox_task

    @property
    def tested_subtask(self):
        # XXX - This rotates out as we have more than 5 in the fixture
        # XXX - not expected, but a quick way around the visibility limit
        return self.private_task

    @property
    def participants(self):
        return [u'B\xe4rfuss K\xe4thi (kathi.barfuss)',
                u'Ziegler Robert (robert.ziegler)']

    @property
    def task_titles(self):
        # XXX - These rotate out as we have more than 5 in the fixture
        return [
            u're: Diskr\xe4te Dinge',
            u'Diskr\xe4te Dinge',
            u'Vertragsentw\xfcrfe 2018',
            u'Personaleintritt',
            u'Mitarbeiter Dossier generieren',
        ]

    @property
    def task_titles_minus_pending(self):
        # XXX - These rotate out as we have more than 5 in the fixture
        return [
            u're: Diskr\xe4te Dinge',
            u'Vertragsentw\xfcrfe 2018',
            u'Personaleintritt',
            u'Mitarbeiter Dossier generieren',
            u'Vertragsentwurf \xdcberpr\xfcfen',
        ]

    @browsing
    def test_description_box_is_web_intelligent_formatted_and_xss_safe(self, browser):
        self.login(self.regular_user, browser)

        description = u'Anfrage:\r\n\r\n\r\nhttp://www.example.org/'
        IOpenGeverBase(self.tested_dossier).description = description

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertEqual('Anfrage:\n\n\nhttp://www.example.org/',
                         browser.css('#descriptionBox span').first.text)

        description = u'<img src="http://not.found/" onerror="script:alert(\'XSS\');" />'
        IOpenGeverBase(self.tested_dossier).description = description
        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertEqual(
            u'&lt;img src="http://not.found/" onerror="script:alert(\'XSS\');" /&gt;',
            browser.css('#descriptionBox span').first.innerHTML)

    @browsing
    def test_task_box_items_are_limited_to_five_and_sorted_by_modified(self, browser):
        self.login(self.regular_user, browser=browser)

        for i in range(1, 7):
            create(Builder('task')
                   .within(self.empty_dossier)
                   .titled(u'Task {}'.format(i))
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .having(responsible_client='fa',
                           responsible=self.regular_user.getId(),
                           issuer=self.dossier_responsible.getId(),
                           task_type='correction',
                           deadline=date(2016, 11, 1))
                   .in_state('task-state-in-progress'))

        browser.open(self.empty_dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Task 6', 'Task 5', 'Task 4', 'Task 3', 'Task 2'],
            browser.css('#newest_tasksBox li:not(.moreLink) a').text)

    @browsing
    def test_task_box_items_are_filtered_by_admin_unit(self, browser):
        # create task with same int_id tha
        self.login(self.regular_user, browser=browser)

        create(Builder('globalindex_task').having(
            title=u'Task X', int_id=12345, admin_unit_id='foo',
            issuing_org_unit='foo', sequence_number=4, assigned_org_unit='bar',
            physical_path=self.tested_task.get_sql_object().physical_path,
            modified=date(2011, 1, 1)))

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertSequenceEqual(
            self.task_titles,
            browser.css('#newest_tasksBox li:not(.moreLink) a').text)

    @browsing
    def test_task_box_items_are_filtered_by_pending_state(self, browser):
        self.login(self.regular_user, browser=browser)
        self.set_workflow_state(
            'task-state-tested-and-closed', self.tested_subtask)

        browser.open(self.tested_dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            self.task_titles_minus_pending,
            browser.css('#newest_tasksBox li:not(.moreLink) a').text,
        )

    @browsing
    def test_participant_labels_are_displayed(self, browser):
        self.login(self.regular_user, browser=browser)

        handler = IParticipationAware(self.tested_dossier)
        handler.add_participation('kathi.barfuss', ['regard'])

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertListEqual(
            self.participants,
            browser.css('#participantsBox li:not(.moreLink) a').text)

    @browsing
    def test_contact_participations_are_listed_when_contact_feature_is_enabled(self, browser):
        toggle_feature(IContactSettings, enabled=True)

        self.login(self.regular_user, browser=browser)
        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertEqual(
            [u'B\xfchler Josef', 'Meier AG'],
            browser.css('#participationsBox li:not(.moreLink) a').text)

    @browsing
    def test_task_link_is_safe_html_transformed(self, browser):
        self.login(self.regular_user, browser=browser)
        test_title = u"Foo <script>alert('foo')</script>"
        test_title_safe = 'Foo &lt;script&gt;alert(\'foo\')&lt;/script&gt'
        self.tested_task.get_sql_object().title = test_title

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')

        self.assertEquals(
            [],
            browser.css('span.contenttype-opengever-task-task script'))
        link = browser.find("Foo <script>alert('foo')</script>")
        node = link.css('span').first
        self.assertEquals(
            '<span class="contenttype-opengever-task-task">' +
            test_title_safe + ';</span>',
            tostring(node.node))

    @browsing
    def test_documents_in_overview_are_linked(self, browser):
        self.login(self.regular_user, browser=browser)
        browser.open(self.tested_dossier, view='tabbedview_view-overview')
        links = browser.css('#newest_documentsBox li:not(.moreLink) a.document_link')
        titles = links.text
        anchors = [link.get('href') for link in links]
        self.assertIn(self.tested_document.title, titles)
        self.assertIn(self.tested_document.absolute_url(), anchors)

    @browsing
    def test_document_box_items_are_limited_to_ten_and_sorted_by_modified(self, browser):
        self.login(self.regular_user, browser=browser)

        for i in range(1, 12):
            create(Builder('document')
                   .within(self.empty_dossier)
                   .with_modification_date(DateTime(2010, 1, 1) + i)
                   .titled(u'Document %s' % i))
        self.commit_solr()

        browser.open(self.empty_dossier, view='tabbedview_view-overview')
        self.assertSequenceEqual(
            ['Document 11', 'Document 10', 'Document 9', 'Document 8',
             'Document 7', 'Document 6', 'Document 5', 'Document 4',
             'Document 3', 'Document 2'],
            browser.css('#newest_documentsBox li:not(.moreLink) a.document_link').text)

    @browsing
    def test_references_box_lists_regular_references(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.closed_meeting_dossier,
                     view='tabbedview_view-overview')

        references = browser.css('#referencesBox a')
        self.assertIn(self.tested_dossier.title, references.text)
        self.assertIn(self.tested_dossier.absolute_url(),
                      [link.get('href') for link in references])

    @browsing
    def test_references_box_lists_back_references(self, browser):
        self.login(self.regular_user, browser=browser)

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        references = browser.css('#referencesBox a')
        self.assertEquals([self.closed_meeting_dossier.title],
                          references.text)
        self.assertEquals([self.closed_meeting_dossier.absolute_url()],
                          [link.get('href') for link in references])

    @browsing
    def test_removed_back_refs_are_no_longer_listed(self, browser):
        self.login(self.manager, browser=browser)
        api.content.delete(obj=self.closed_meeting_dossier)
        self.login(self.regular_user, browser=browser)
        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        references = browser.css('#referencesBox a')
        self.assertEquals([], references.text)

    @browsing
    def test_keywords_are_listed_on_overview(self, browser):
        self.login(self.regular_user, browser=browser)

        IDossier(self.tested_dossier).keywords = u'secret', u'special'

        browser.open(self.tested_dossier,
                     view='tabbedview_view-overview')
        self.assertEquals([u'secret', u'special'],
                          browser.css('#keywordsBox li span').text)

    @browsing
    def test_related_dossiers_are_listed_on_overview(self, browser):
        self.login(self.regular_user, browser=browser)
        intids = getUtility(IIntIds)
        relations = IDossier(self.closed_meeting_dossier).relatedDossier
        relations.append(RelationValue(intids.getId(self.subdossier)))
        titles = ["abc", "Abd", "bcd"]

        for relation, title in zip(relations, titles):
            relation.to_object.setTitle(title)
        browser.open(self.closed_meeting_dossier,
                     view='tabbedview_view-overview')
        self.assertEqual(titles, [node.text for node in
                                  browser.css("#referencesBox li span")])

        for relation, title in zip(relations, reversed(titles)):
            relation.to_object.setTitle(title)
        browser.open(self.closed_meeting_dossier, view='tabbedview_view-overview')
        self.assertEqual(titles, [node.text for node in
                                  browser.css("#referencesBox li span")])
