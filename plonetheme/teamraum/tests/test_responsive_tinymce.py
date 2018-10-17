from plonetheme.teamraum.browser.style import TINYMCE_BANNED_STYLES
from plonetheme.teamraum.testing import TeamraumThemeTestCase
from Products.Five.utilities.marker import mark
from Products.TinyMCE.interfaces.utility import ITinyMCE


class TestCustomStyles(TeamraumThemeTestCase):

    def test_banned_styles_not_in_tinymce(self):
        mark(self.portal, ITinyMCE)
        view = self.portal.restrictedTraverse('tinymce-getstyle')()
        for banned_style in TINYMCE_BANNED_STYLES:
            self.assertNotIn(banned_style, view)
