from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase
from plone import api
from zope.component import getMultiAdapter


class TestGeverLayoutPolicy(IntegrationTestCase):

    @browsing
    def test_bumblebee_feature(self, browser):
        self.login(self.regular_user, browser)
        feature_class = 'feature-bumblebee'

        self.deactivate_feature('bumblebee')
        browser.open()
        self.assertNotIn(feature_class, browser.css('body').first.classes)

        self.activate_feature('bumblebee')
        browser.open()
        self.assertIn(feature_class, browser.css('body').first.classes)

    @browsing
    def test_word_meeting_feature_presence(self, browser):
        self.login(self.regular_user, browser)

        feature_class = 'feature-word-meeting'

        self.activate_feature('meeting')
        browser.open()
        self.assertIn(feature_class, browser.css('body').first.classes)

        self.deactivate_feature('meeting')
        browser.open()
        self.assertNotIn(feature_class, browser.css('body').first.classes)

    @browsing
    def test_no_model_class_on_regular_content(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier)
        self.assertEquals([],
                          filter(lambda classname: classname.startswith('model-'),
                                 browser.css('body').first.classes))

    @browsing
    def test_model_class_on_sql_wrapper(self, browser):
        self.login(self.committee_responsible, browser)
        self.activate_feature('meeting')
        browser.open(self.meeting)
        self.assertIn('model-meeting', browser.css('body').first.classes)

    def test_render_base_returns_correct_url(self):
        self.login(self.manager)
        portal = api.portal.get()
        contents = api.content.find(context=portal)
        portal_types = set(el.portal_type for el in contents)
        for portal_type in portal_types:
            brains = api.content.find(portal_type=portal_type)
            obj = brains[0].getObject()
            layout = getMultiAdapter((obj, self.request), name=u'plone_layout')
            self.assertEqual(layout.renderBase(), obj.absolute_url().rstrip("/") + "/")
