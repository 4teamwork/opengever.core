from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.webactions.interfaces import IWebActionsRenderer
from opengever.webactions.renderer import WebActionsSafeDataGetter
from opengever.webactions.storage import ALLOWED_QUERY_PLACEHOLDERS
from opengever.webactions.storage import DEFAULT_QUERY_PARAMS
from plone.uuid.interfaces import IUUID
from urllib import urlencode
from urlparse import parse_qs
from urlparse import urlparse
from zope.component import getMultiAdapter


class TestWebActionRendererTitleButtons(IntegrationTestCase):

    display = 'title-buttons'
    icon = 'fa-helicopter'
    adapter_interface = IWebActionsRenderer

    params = {'context': 'http://nohost/plone/ordnungssystem/fuhrung'
              '/vertrage-und-vereinbarungen/dossier-1',
              'orgunit': 'fa'}

    expected_data = [
        '<a title="Action 1" href="http://example.org/endpoint?{}" '
        'class="webaction_button fa fa-helicopter"></a>'.format(urlencode(params)),

        '<a title="Action 2" href="http://example.org/endpoint?{}" '
        'class="webaction_button fa fa-helicopter"></a>'.format(urlencode(params))]

    def setUp(self):
        super(TestWebActionRendererTitleButtons, self).setUp()
        create(Builder('webaction')
               .titled(u'Action 1')
               .having(order=5, enabled=True, display=self.display, icon_name=self.icon))

        create(Builder('webaction')
               .titled(u'Action 2')
               .having(order=10, enabled=True, display=self.display, icon_name=self.icon))

    def test_data_returned_by_webaction_renderer(self):
        self.login(self.regular_user)
        renderer = getMultiAdapter((self.dossier, self.request),
                                   self.adapter_interface,
                                   name=self.display)
        rendered_data = renderer()

        self.assertEqual(self.expected_data, rendered_data)


class TestWebActionRendererActionButtons(TestWebActionRendererTitleButtons):

    display = 'action-buttons'
    icon = 'fa-helicopter'

    params = {'context': 'http://nohost/plone/ordnungssystem/fuhrung'
              '/vertrage-und-vereinbarungen/dossier-1',
              'orgunit': 'fa'}

    expected_data = [
            '<a title="Action 1" href="http://example.org/endpoint?{}" '
            'class="webaction_button fa fa-helicopter">'
            '<span class="subMenuTitle actionText">Action 1</span></a>'.format(
              urlencode(params)),

            '<a title="Action 2" href="http://example.org/endpoint?{}" '
            'class="webaction_button fa fa-helicopter">'
            '<span class="subMenuTitle actionText">Action 2</span></a>'.format(
              urlencode(params))]


class TestWebActionRendererTargetUrl(IntegrationTestCase):
    display = 'actions-menu'

    def _get_querystring_params(self):
        data_getter = WebActionsSafeDataGetter(self.dossier, self.request,
                                               self.display)

        data = data_getter.get_webactions_data()
        target_url = data['actions-menu'][0]['target_url']
        return parse_qs(urlparse(target_url).query)

    def test_default_querystring_parameter(self):
        create(Builder('webaction')
               .having(display=self.display))
        self.login(self.regular_user)
        query = self._get_querystring_params()
        self.assertEqual(2, len(query))
        self.assertEqual(
            ['fa'],
            query['orgunit']
        )
        self.assertEqual(
            [self.dossier.absolute_url()],
            query['context']
        )

    def test_target_url_querystring_placeholder_uid(self):
        create(Builder('webaction')
               .having(target_url='http://localhost/foo?geverid={uid}'), display=self.display)
        self.login(self.regular_user)
        query = self._get_querystring_params()
        self.assertEqual(
            [IUUID(self.dossier)],
            query['geverid']
        )

    def test_target_url_querystring_placeholder_path(self):
        create(Builder('webaction')
               .having(target_url='http://localhost/foo?location={path}'), display=self.display)
        self.login(self.regular_user)
        query = self._get_querystring_params()
        self.assertEqual(
            ['/plone/ordnungssystem/fuhrung/vertrage-und-vereinbarungen/dossier-1'],
            query['location']
        )

    def test_target_url_querystring_placeholder_intid(self):
        create(Builder('webaction')
               .having(target_url='http://localhost/foo?geverid={intid}'), display=self.display)
        self.login(self.regular_user)
        query = self._get_querystring_params()
        self.assertEqual(
            ['1014013300'],
            query['geverid']
        )

    def test_target_url_query_param_escapes_html(self):
        create(Builder('webaction')
               .having(target_url='http://localhost/foo?some<html>thing={intid}&evil=<script>'), display=self.display)
        self.login(self.regular_user)
        data_getter = WebActionsSafeDataGetter(
            self.dossier, self.request, self.display
        )

        data = data_getter.get_webactions_data()
        target_url = data['actions-menu'][0]['target_url']

        self.assertEqual(
            'http://localhost/foo'
            '?some%26lt%3Bhtml%26gt%3Bthing=1014013300'
            '&evil=%26lt%3Bscript%26gt%3B'
            '&context=http%3A%2F%2Fnohost%2Fplone%2Fordnungssystem%2Ffuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1'
            '&orgunit=fa',
            target_url
        )

    def test_target_url_renderer_knows_all_default_query_params(self):
        """
        This test makes sure that a developer does not forget to update the
        implementation when new default query parameters are added (and vice
        versa).
        """
        self.login(self.regular_user)
        data_getter = WebActionsSafeDataGetter(
            self.dossier, self.request, self.display
        )
        self.assertEqual(
            DEFAULT_QUERY_PARAMS,
            data_getter._get_default_webaction_parameters().keys(),
            msg='The config "DEFAULT_QUERY_PARAMS" is out of sync with the implementation.',
        )

    def test_adding_webaction_with_all_allowed_params(self):
        """
        This test makes sure that a developer does not forget to update the
        implementation when new allowed query placeholder are added (and vice
        versa).
        """
        params = ["{}={}".format(name, value) for name, value in enumerate(ALLOWED_QUERY_PLACEHOLDERS, 1)]
        create(Builder('webaction')
               .having(target_url='http://localhost/foo?' + '&'.join(params)), display=self.display)
        self.login(self.regular_user)
        data_getter = WebActionsSafeDataGetter(
            self.dossier, self.request, self.display
        )

        data = data_getter.get_webactions_data()
        target_url = data['actions-menu'][0]['target_url']

        self.assertEqual(
            'http://localhost/foo'
            '?1=1014013300'  # intid
            '&3=createtreatydossiers000000000001'  # uid
            '&2=%2Fplone%2Fordnungssystem%2Ffuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1'  # path
            '&context=http%3A%2F%2Fnohost%2Fplone%2Fordnungssystem%2Ffuhrung%2Fvertrage-und-vereinbarungen%2Fdossier-1'
            '&orgunit=fa',
            target_url,
            msg='The config "ALLOWED_QUERY_PLACEHOLDERS" is out of sync with the implementation.',
        )
