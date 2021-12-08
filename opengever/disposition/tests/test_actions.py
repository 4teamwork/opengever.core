from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.lifecycle import ARCHIVAL_VALUE_SAMPLING
from opengever.base.behaviors.lifecycle import ILifeCycle
from opengever.base.security import elevated_privileges
from opengever.testing import IntegrationTestCase
import os
from plone import api
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue


class TestDispositionActions(IntegrationTestCase):

    @browsing
    def test_download_appraisal_list_only_available_on_dipsositions(self, browser):
        self.login(self.records_manager, browser)

        browser.open(u'{}/@actions'.format(self.disposition.absolute_url()),
                     headers=self.api_headers)
        self.assertIn(
            'download-appraisal-list',
            [action['id'] for action in browser.json['ui_context_actions']])

        browser.open(u'{}/@actions'.format(self.dossier.absolute_url()),
                     headers=self.api_headers)
        self.assertNotIn(
            'download-appraisal-list',
            [action['id'] for action in browser.json['ui_context_actions']])

    @browsing
    def test_download_sip_available_if_sip_exist(self, browser):
        self.login(self.records_manager, browser)

        # without sip
        browser.open(u'{}/@actions'.format(self.disposition.absolute_url()),
                     headers=self.api_headers)
        self.assertNotIn(
            'download-sip',
            [action['id'] for action in browser.json['ui_context_actions']])

        # with sip
        browser.open(
            u'{}/@actions'.format(self.disposition_with_sip.absolute_url()),
            headers=self.api_headers)
        self.assertIn(
            'download-sip',
            [action['id'] for action in browser.json['ui_context_actions']])

        # only for dispositions
        browser.open(u'{}/@actions'.format(self.dossier.absolute_url()),
                     headers=self.api_headers)
        self.assertNotIn(
            'download-sip',
            [action['id'] for action in browser.json['ui_context_actions']])

    @browsing
    def test_download_removal_protocol_only_available_for_closed_dispositions(self, browser):
        self.login(self.records_manager, browser)
        url = u'{}/@actions'.format(self.disposition_with_sip.absolute_url())

        browser.open(url, headers=self.api_headers)
        self.assertNotIn(
            'download-removal-protocol',
            [action['id'] for action in browser.json['ui_context_actions']])

        self.set_workflow_state('disposition-state-closed',
                                self.disposition_with_sip)

        browser.open(url, headers=self.api_headers)
        self.assertIn(
            'download-removal-protocol',
            [action['id'] for action in browser.json['ui_context_actions']])
