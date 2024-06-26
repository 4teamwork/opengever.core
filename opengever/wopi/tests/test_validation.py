"""
This test runs Microsofts WOPI validator
https://github.com/Microsoft/wopi-validator-core

Currently only the tests in the category WOPICore are executed because the
ProofKey tests do not pass.
https://github.com/microsoft/wopi-validator-core/issues/22

The test requires Docker, thus it's only executed if a docker binary is found.

With Docker Desktop (macOS) the ZServer needs to listen on all interfaces to be
accessible from the Docker container. This can be acomplished by setting the
environment variable ZSERVER_HOST before executing the test:
`export ZSERVER_HOST="0.0.0.0"`
"""

from base64 import urlsafe_b64encode
from distutils.spawn import find_executable
from ftw.builder import Builder
from ftw.builder import create
from mock import patch
from opengever.core.testing import OPENGEVER_FUNCTIONAL_ZSERVER_TESTING
from opengever.testing.test_case import FunctionalTestCase
from opengever.wopi.token import create_access_token
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.uuid.interfaces import IUUID
from unittest import skipIf
import os
import subprocess
import sys
import transaction


HAS_DOCKER = find_executable('docker')
ZSERVER_HOST = os.environ.get('ZSERVER_HOST')


@skipIf(
    not sys.platform.startswith('linux') and ZSERVER_HOST != '0.0.0.0',
    'ZServer must bind on all interfaces.',
)
@skipIf(not HAS_DOCKER, 'Docker is required for WOPI validation.')
class TestWOPIValidation(FunctionalTestCase):

    layer = OPENGEVER_FUNCTIONAL_ZSERVER_TESTING

    def test_run_validator(self):
        portal = self.layer["portal"]
        repo = create(Builder("repository_root"))
        repofolder = create(Builder("repository").within(repo))
        dossier = create(Builder("dossier").within(repofolder))
        document = create(
            Builder("document")
            .within(dossier)
            .attach_file_containing(b"DUMMY", u"wopi-test.wopitest")
        )
        setRoles(self.portal, TEST_USER_ID,
                 ['Contributor', 'Editor', 'Member', 'Reader'])
        transaction.commit()

        uuid = IUUID(document)
        access_token = urlsafe_b64encode(
            create_access_token(TEST_USER_ID, uuid))

        portal_url = portal.absolute_url()
        if ZSERVER_HOST == '0.0.0.0':
            portal_url = portal_url.replace('0.0.0.0', 'host.docker.internal').replace(
                'localhost', 'host.docker.internal')

        url = '%s/wopi/files/%s' % (portal_url, uuid)
        cmd = [
            'docker',
            'run',
            '-t',
            '--rm',
            'tylerbutler/wopi-validator',
            '--',
            '-w',
            url,
            '-t',
            access_token,
            '-l',
            '0',
            '-s',
            '-e',
            'WopiCore',
        ]

        # If ZServer is not bound to all interfaces, we need to use the host
        # network for Docker. This is only supported on Linux.
        if not ZSERVER_HOST:
            cmd[4:4] = ['--network', 'host']

        # Disable proof key validation as long as it's not supported by
        # wopi-validator-core
        with patch(
            'opengever.wopi.browser.wopi.validate_wopi_proof'
        ) as mocked_validate_wopi_proof:
            mocked_validate_wopi_proof.return_value = True
            try:
                output = subprocess.check_output(cmd)
                print(output)
            except subprocess.CalledProcessError as exc:
                output = exc.output
                self.fail(output)
        self.assertIn('Pass', output, 'Has passed tests')
        self.assertNotIn('Fail', output, 'Has no failed tests')
