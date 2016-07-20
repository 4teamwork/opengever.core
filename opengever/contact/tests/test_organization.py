from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestOrganization(FunctionalTestCase):

    def test_get_url_returns_url_for_wrapper_object(self):
        create(Builder('contactfolder'))

        org1 = create(Builder('organization').named(u'Meier AG'))
        org2 = create(Builder('organization').named(u'4teamwork AG'))

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/organization-1/view',
            org1.get_url())
        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/organization-2/edit',
            org2.get_url(view='edit'))
