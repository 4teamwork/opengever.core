from datetime import datetime
from ftw.builder.builder import Builder
from ftw.builder.builder import create
from ftw.testbrowser import browsing
from ftw.testing import freeze
from opengever.dossier.behaviors.dossier import IDossier
from opengever.testing import IntegrationTestCase
from plone import api


class TestDossierTouched(IntegrationTestCase):

    @browsing
    def test_touched_date_is_set_correctly_on_new_dossiers(self, browser):
        self.login(self.regular_user, browser)
        with freeze(datetime(2020, 6, 12)):
            dossier = create(Builder("dossier")
                             .within(self.leaf_repofolder))
            self.assertEqual("2020-06-12", str(IDossier(dossier).touched))

    @browsing
    def test_touched_date_is_only_updated_when_set_to_different_date(self, browser):
        self.login(self.administrator, browser=browser)

        # Multiple modifications on the same day result in the same touched date.
        with freeze(datetime(2020, 6, 12)):
            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "First modification"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))

            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "Modification on the same day"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))

        # Modifications on the next day will change the "touched" date.
        with freeze(datetime(2020, 6, 13)):
            browser.open(self.dossier, view="edit")
            browser.fill({u"Title": "Modification on the next day"}).save()
            self.assertEqual("2020-06-13", str(IDossier(self.dossier).touched))

    @browsing
    def test_modifying_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            browser.open(self.subdocument, view="edit")
            browser.fill({u"Title": "Modified subdocument"}).save()
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))

    @browsing
    def test_adding_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            create(Builder('document').within(self.subdossier))
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))

    @browsing
    def test_deleting_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.manager, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subsubdossier).touched))

        with freeze(datetime(2020, 6, 12)):
            api.content.delete(obj=self.subsubdocument)
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subsubdossier).touched))

    @browsing
    def test_moving_content_touches_all_dossiers_in_path(self, browser):
        self.login(self.administrator, browser=browser)

        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier2).touched))

        with freeze(datetime(2020, 6, 12)):
            api.content.move(source=self.subdocument, target=self.subdossier2)
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier2).touched))

    @browsing
    def test_modifying_proposal_touches_containing_dossier(self, browser):
        self.activate_feature('meeting')

        self.login(self.administrator, browser)
        self.assertEqual("2016-08-31", str(IDossier(self.empty_dossier).touched))

        with freeze(datetime(2020, 6, 12)):
            proposal = create(Builder('proposal')
                              .within(self.empty_dossier)
                              .titled(u'My Proposal')
                              .having(committee=self.committee.load_model()))
            self.assertEqual("2020-06-12", str(IDossier(self.empty_dossier).touched))

        with freeze(datetime(2020, 6, 13)):
            browser.open(proposal, view="edit")
            browser.fill({u"Title": "Modified proposal"}).save()
            self.assertEqual("2020-06-13", str(IDossier(self.empty_dossier).touched))

    @browsing
    def test_changing_state_of_proposal_touches_containing_dossier(self, browser):
        self.activate_feature('meeting')

        self.login(self.administrator, browser)
        self.assertEqual("2016-08-31", str(IDossier(self.empty_dossier).touched))

        with freeze(datetime(2020, 6, 12)):
            proposal = create(Builder('proposal')
                              .within(self.empty_dossier)
                              .titled(u'My Proposal')
                              .having(committee=self.committee.load_model()))
            self.assert_workflow_state('proposal-state-active', proposal)
            self.assertEqual("2020-06-12", str(IDossier(self.empty_dossier).touched))

        with freeze(datetime(2020, 6, 13)):
            browser.open(proposal, view='tabbedview_view-overview')
            browser.click_on("proposal-transition-cancel")
            browser.click_on("Confirm")
            self.assert_workflow_state('proposal-state-cancelled', proposal)

            self.assertEqual("2020-06-13", str(IDossier(self.empty_dossier).touched))

    @browsing
    def test_changing_state_of_subdossier_touches_containing_dossier(self, browser):
        self.login(self.administrator, browser)
        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))
        self.assertEqual("2016-08-31", str(IDossier(self.subdossier).touched))
        self.assert_workflow_state('dossier-state-active', self.subdossier)

        with freeze(datetime(2020, 6, 12)):
            browser.open(self.subdossier)
            browser.click_on("dossier-transition-resolve")
            self.assert_workflow_state('dossier-state-resolved', self.subdossier)
            self.assertEqual("2020-06-12", str(IDossier(self.dossier).touched))
            self.assertEqual("2020-06-12", str(IDossier(self.subdossier).touched))

    @browsing
    def test_changing_state_of_task_touches_containing_dossier(self, browser):
        self.login(self.administrator, browser)
        self.set_workflow_state('task-state-open', self.task)  # So we can cancel it later.
        self.assertEqual("2016-08-31", str(IDossier(self.dossier).touched))

        with freeze(datetime(2020, 6, 13)):
            browser.open(self.task)
            browser.click_on("task-transition-open-cancelled")
            browser.click_on("Save")

            self.assert_workflow_state('task-state-cancelled', self.task)
            self.assertEqual("2020-06-13", str(IDossier(self.dossier).touched))
