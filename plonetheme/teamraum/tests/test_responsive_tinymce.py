from Products.Five.utilities.marker import mark
from Products.TinyMCE.interfaces.utility import ITinyMCE
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plonetheme.teamraum.browser.style import TINYMCE_BANNED_STYLES
from plonetheme.teamraum.testing import TEAMRAUMTHEME_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestCustomStyles(TestCase):

    layer = TEAMRAUMTHEME_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_banned_styles_not_in_tinymce(self):
        mark(self.portal, ITinyMCE)
        view = self.portal.restrictedTraverse('tinymce-getstyle')()
        for banned_style in TINYMCE_BANNED_STYLES:
            self.assertNotIn(banned_style, view)
