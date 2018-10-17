from ftw.testbrowser import browsing
from opengever.testing import IntegrationTestCase


class TestPastingAllowed(IntegrationTestCase):

    @browsing
    def test_paste_action_not_displayed_for_contactfolder(self, browser):
        self.login(self.regular_user, browser)
        paths = ['/'.join(self.hanspeter_duerr.getPhysicalPath())]
        browser.open(self.contactfolder, data={'paths:list': paths}, view='copy_items')
        browser.open(self.contactfolder)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual([], actions)

    @browsing
    def test_paste_action_displayed_for_templates(self, browser):
        self.login(self.administrator, browser)
        paths = ['/'.join(self.normal_template.getPhysicalPath())]
        browser.open(self.templates, data={'paths:list': paths}, view='copy_items')
        browser.open(self.templates)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(['Export as Zip', 'Paste', 'Properties', 'Sharing'], actions)

    @browsing
    def test_pasting_template_into_template_folder_is_allowed(self, browser):
        self.login(self.administrator, browser)
        paths = ['/'.join(self.normal_template.getPhysicalPath())]
        browser.open(self.templates, data={'paths:list': paths}, view='copy_items')
        browser.open(self.templates, view='is_pasting_allowed')
        self.assertTrue(browser.contents)

    @browsing
    def test_paste_action_not_displayed_for_mails(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, {'paths:list': ['/'.join(self.document.getPhysicalPath())]}, view='copy_items')
        browser.open(self.mail_eml)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(['Copy Item', 'Properties', 'save attachments'], actions)

    @browsing
    def test_pasting_not_allowed_if_disallowed_subobject_type(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, data={'paths:list': ['/'.join(self.document.getPhysicalPath())]}, view='copy_items',)
        browser.open(self.leaf_repofolder, view='is_pasting_allowed')
        self.assertFalse(browser.contents)

    @browsing
    def test_pasting_public_content_into_private_container_is_disallowed(self, browser):
        self.login(self.regular_user, browser)
        browser.open(self.dossier, data={'paths:list': ['/'.join(self.document.getPhysicalPath())]}, view='copy_items')
        browser.open(self.private_dossier, view='is_pasting_allowed')
        self.assertFalse(browser.contents)

    @browsing
    def test_pasting_private_content_into_private_container_is_allowed(self, browser):
        self.login(self.regular_user, browser)
        paths = ['/'.join(self.private_document.getPhysicalPath())]
        browser.open(self.private_dossier, data={'paths:list': paths}, view='copy_items')
        browser.open(self.private_dossier, view='is_pasting_allowed')
        self.assertTrue(browser.contents)
