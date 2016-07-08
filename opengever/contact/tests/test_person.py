from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import FunctionalTestCase


class TestPerson(FunctionalTestCase):

    def test_get_url_returns_url_for_wrapper_object(self):
        create(Builder('contactfolder'))

        peter = create(Builder('person')
                       .having(firstname=u'Peter', lastname=u'M\xfcller'))
        sandra = create(Builder('person')
                        .having(firstname=u'Sandra', lastname=u'Meier'))

        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/person-1/view',
            peter.get_url())
        self.assertEquals(
            'http://nohost/plone/opengever-contact-contactfolder/person-2/edit',
            sandra.get_url(view='edit'))
