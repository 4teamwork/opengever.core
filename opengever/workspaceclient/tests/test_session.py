from datetime import datetime
from ftw.builder import Builder
from ftw.builder import create
from ftw.tokenauth.pas.storage import CredentialStorage
from opengever.workspaceclient.session import GEVER_VERSION
from opengever.workspaceclient.session import WorkspaceSession
from opengever.workspaceclient.tests import FunctionalWorkspaceClientTestCase
from plone import api
from plone.app.testing import TEST_USER_ID
from requests import HTTPError
import requests_mock
import transaction


class TestWorkspaceSessionManager(FunctionalWorkspaceClientTestCase):

    def test_prepare_authenticated_session_object(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        session = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)

        self.assertIn('Bearer ',
                      session.session.headers.get('Authorization'))
        self.assertEqual('application/json',
                         session.session.headers.get('Accept'))

    def test_make_requests_with_the_session(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        session = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)

        response = session.request.get('/').json()

        self.assertEqual(self.portal.absolute_url(), response.get('@id'))

    def test_auto_renew_access_token_if_expired(self):
        def extract_jwt_token(session):
            return session.session.headers.get('Authorization').split(' ')[-1]

        plugin = api.portal.get_tool('acl_users')['token_auth']
        storage = CredentialStorage(plugin)
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        # Make a new session will create a jwt-token for the current session
        session = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)
        jwt_token = extract_jwt_token(session)
        transaction.commit()

        # Making a request with the same session will reuse the jwt_token
        response = session.request.get('/').json()
        self.assertEqual(jwt_token, extract_jwt_token(session),
                         "JWT token should still be the same")

        # Set access token as expired
        access_token = storage.get_access_token(jwt_token)
        access_token['issued'] = datetime(2018, 1, 1, 15, 30)
        transaction.commit()

        # Making a request with an expired token will auto-renew the jwt-token
        response = session.request.get('/').json()
        self.assertNotEqual(jwt_token, extract_jwt_token(session),
                            "JWT should have been renewed")
        self.assertEqual(self.portal.absolute_url(), response.get('@id'))

    def test_error_when_key_invalid(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        with requests_mock.Mocker() as mocker:
            mocker.post('{}/@@oauth2-token'.format(self.portal.absolute_url()),
                        status_code=500)
            with self.assertRaises(HTTPError) as cm:
                WorkspaceSession(self.portal.absolute_url(), 'john.doe')

        self.maxDiff = None
        self.assertEqual(
            '500 Server Error: None for url: {}/@@oauth2-token'.format(self.portal.absolute_url()),
            str(cm.exception))

    def test_user_agent(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        manager = WorkspaceSession(self.portal.absolute_url(), self.service_user.getId())
        self.assertEqual(
            manager.session.headers.get('User-Agent'),
            'opengever.core/{}'.format(GEVER_VERSION))

    def test_user_agent_is_configurable(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        with self.env(OPENGEVER_APICLIENT_USER_AGENT='Baumverwaltung/7.0'):
            manager = WorkspaceSession(self.portal.absolute_url(), self.service_user.getId())
            self.assertEqual(
                manager.session.headers.get('User-Agent'),
                'opengever.core/{} Baumverwaltung/7.0'.format(GEVER_VERSION))

    def test_unique_session_for_each_user(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        session_1 = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)
        session_2 = WorkspaceSession(self.portal.absolute_url(), self.service_user.getId())

        self.assertIsNot(session_1.session, session_2.session)

    def test_reuse_session(self):
        create(Builder('workspace_token_auth_app')
               .issuer(self.service_user)
               .uri(self.portal.absolute_url()))
        transaction.commit()

        session_1 = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)
        session_2 = WorkspaceSession(self.portal.absolute_url(), TEST_USER_ID)

        self.assertIs(session_1.session, session_2.session)
