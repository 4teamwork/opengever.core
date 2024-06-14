
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from zope.event import notify
from zope.lifecycleevent import modified


class TestHandleEvaluationFinalize(IntegrationTestCase):

    @browsing
    def test_responsible_is_set_on_success(self, browser):
        self.login(self.archivist, browser)
        disposition = create(Builder('disposition'))
        api.content.transition(obj=disposition,
                               transition='disposition-transition-appraise')
        notify(modified(disposition))
        self.assertEqual(disposition.responsible, self.archivist.id)

    @browsing
    def test_responsible_is_not_changed_if_already_set(self, browser):
        self.login(self.archivist, browser)
        disposition = create(Builder('disposition').having(responsible=self.administrator.id))
        initial_responsible = disposition.responsible
        api.content.transition(obj=disposition,
                               transition='disposition-transition-appraise')
        notify(modified(disposition))
        self.assertEqual(disposition.responsible, initial_responsible)
