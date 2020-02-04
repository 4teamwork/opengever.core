from contextlib import contextmanager
from ftw.builder import Builder
from ftw.builder import create
from opengever.testing import IntegrationTestCase
from opengever.workspaceclient.exceptions import ServiceKeyMissing
from opengever.workspaceclient.keys import key_registry
from plone.restapi.serializer.converters import json_compatible
import json
import shutil
import tempfile


class TestKeyRegistry(IntegrationTestCase):

    @contextmanager
    def temp_fs_key(self, key):
        temp_dir = tempfile.mkdtemp()
        original_key_directory = key_registry.key_directory
        key_registry.key_directory = temp_dir
        file_ = tempfile.NamedTemporaryFile(
            dir=temp_dir, suffix=".json", delete=False)
        file_.write(json.dumps(json_compatible(key)))
        file_.close()
        try:
            yield temp_dir
        finally:
            shutil.rmtree(temp_dir)
            key_registry.key_directory = original_key_directory

    def test_raises_an_error_if_the_key_file_not_found_for_a_specific_url(self):
        service_key_client = create(Builder('workspace_token_auth_app')
                                    .uri('http://example.com/plone/'))
        with self.temp_fs_key(service_key_client) as path:
            with self.assertRaises(ServiceKeyMissing) as cm:
                key_registry.get_key_for('http://example.de/plone/')

            self.maxDiff = None
            self.assertEqual(
                "No workspace service key found for URL http://example.de/plone.\n"
                "Found keys ('http://example.com/plone',) in the folder: {}".format(path),
                str(cm.exception))

    def test_skip_fs_keys_without_a_token_uri(self):
        service_key_client = create(Builder('workspace_token_auth_app')
                                    .uri('http://example.com/plone/'))

        del service_key_client['token_uri']
        with self.temp_fs_key(service_key_client):
            key_registry.load_file_system_keys()
            self.assertEqual([], key_registry.keys)

    def test_return_registered_keys_on_the_filesystem(self):
        service_key_client = create(Builder('workspace_token_auth_app')
                                    .uri('http://example.com/plone'))
        with self.temp_fs_key(service_key_client):
            self.assertEqual(
                ['http://example.com/plone'],
                key_registry.keys_by_token_uri.keys())

    def test_get_key_for(self):
        service_key_client = create(Builder('workspace_token_auth_app')
                                    .uri('http://example.com/plone/'))
        self.assertDictContainsSubset(
            service_key_client,
            key_registry.get_key_for('http://example.com/plone/'))
