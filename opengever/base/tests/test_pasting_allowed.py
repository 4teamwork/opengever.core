from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.testing import FunctionalTestCase


class TestPastingAllowed(FunctionalTestCase):

    @browsing
    def test_paste_action_not_displayed_for_contactfolder(self, browser):
        contactfolder = create(Builder('contactfolder'))
        contact = create(Builder('contact')
                         .within(contactfolder))

        paths = ['/'.join(contact.getPhysicalPath())]
        browser.login().open(contactfolder, {'paths:list': paths},
                             view='copy_items')

        browser.open(contactfolder)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual([], actions)

    @browsing
    def test_paste_action_not_displayed_for_templatefolder(self, browser):
        templatefolder = create(Builder('templatefolder'))
        document = create(Builder('document')
                          .within(templatefolder))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(templatefolder, {'paths:list': paths},
                             view='copy_items')

        browser.open(templatefolder)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(
            ['Export as Zip', 'Properties'], actions)

    @browsing
    def test_paste_action_not_displayed_for_mails(self, browser):
        dossier = create(Builder('dossier'))
        document = create(Builder('document').within(dossier))
        mail = create(Builder('mail').within(dossier))

        paths = ['/'.join(document.getPhysicalPath())]
        browser.login().open(dossier, {'paths:list': paths}, view='copy_items')

        browser.open(mail)
        actions = browser.css('#plone-contentmenu-actions li').text
        self.assertSequenceEqual(
            ['Copy Item', 'Properties', 'save attachments'], actions)

    @browsing
    def test_pasting_not_allowed_if_disallowed_subobject_type(self, browser):
        repofolder = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repofolder))
        document = create(Builder('document').within(dossier))

        browser.login().open(
            dossier,
            view='copy_items',
            data={'paths:list': ['/'.join(document.getPhysicalPath())]})

        browser.open(repofolder, view='is_pasting_allowed')
        self.assertFalse(browser.contents)

    @browsing
    def test_pasting_public_content_into_private_container_is_disallowed(self, browser):
        repo = create(Builder('repository'))
        dossier = create(Builder('dossier').within(repo))
        document = create(Builder('document').within(dossier))

        private_root = create(Builder('private_root'))
        private_folder = create(Builder('private_folder').within(private_root))
        private_dossier = create(Builder('private_dossier').within(private_folder))

        browser.login().open(
            dossier,
            view='copy_items',
            data={'paths:list': ['/'.join(document.getPhysicalPath())]})

        browser.open(private_dossier, view='is_pasting_allowed')
        self.assertFalse(browser.contents)

    @browsing
    def test_pasting_private_content_into_private_container_is_allowed(self, browser):
        private_root = create(Builder('private_root'))
        private_folder = create(Builder('private_folder').within(private_root))
        dossier_1 = create(Builder('private_dossier').within(private_folder))
        document = create(Builder('document').within(dossier_1))
        dossier_2 = create(Builder('private_dossier').within(private_folder))

        browser.login().open(
            dossier_1,
            view='copy_items',
            data={'paths:list': ['/'.join(document.getPhysicalPath())]})

        browser.open(dossier_2, view='is_pasting_allowed')
        self.assertTrue(browser.contents)
