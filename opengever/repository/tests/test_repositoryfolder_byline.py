from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from opengever.base.behaviors.classification import PRIVACY_LAYER_NO
from opengever.base.tests.byline_base_test import TestBylineBase
from opengever.testing import create_ogds_user
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestRepositoryfolderByline(TestBylineBase):

    def setUp(self):
        super(TestRepositoryfolderByline, self).setUp()

        self.intids = getUtility(IIntIds)

        create_ogds_user('hugo.boss')

        self.repo = create(Builder('repository')
               .in_state('repositoryfolder-state-active')
               .having(privacy_layer=PRIVACY_LAYER_NO))

    @browsing
    def test_repository_byline_privacy_layer_display(self, browser):
        browser.login().open(self.repo)

        privacy_layer = self.get_byline_value_by_label('Privacy layer:')
        self.assertEquals('privacy_layer_no', privacy_layer.text)

    @browsing
    def test_repository_byline_public_trial_is_not_present(self, browser):
        browser.login().open(self.repo)

        public_trial = self.get_byline_value_by_label('Public Trial:')
        self.assertIsNone(
            public_trial,
            "Public trial must NOT be part of repository byline any more")

    @browsing
    def test_description_is_shown_when_exists(self, browser):
        self.repo.description = u'Etiam ultricies nisi vel augue.'
        transaction.commit()

        browser.login().open(self.repo)

        self.assertEquals([u'Etiam ultricies nisi vel augue.'],
                          browser.css('.documentByLine .description').text)

    @browsing
    def test_description_div_is_not_shown_when_no_description_exist(self, browser):
        browser.login().open(self.repo)

        self.assertEquals([], browser.css('.documentByLine .description'))
