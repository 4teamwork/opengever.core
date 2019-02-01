from os.path import join as pjoin
from os.path import normpath
from os.path import relpath
from pkg_resources import resource_filename
import fnmatch
import hashlib
import os
import pprint
import re
import unittest


class TestJSCacheInvalidation(unittest.TestCase):
    """Test that poor mans cache invalidation information is updated.

    Test that cache invalidation parameters for manually included javscripts
    are updated whenever the file changes.

    May not catch all manual includes but is hopefully better than nothing.
    """
    maxDiff = None

    # we don't have a naming convention, some packages deviate from the
    # package/name/browser/resources naming scheme.
    resource_dir_to_path_segments = {
        'opengever.workspace.participants.resources':
            ('opengever', 'workspace', 'participation', 'browser', 'resources',),
        'opengever.document':
            ('opengever', 'document', 'static',),
    }
    og_core_package_path = normpath(pjoin(
            resource_filename('opengever.core', ''), '..', '..'))
    og_namespace_path = pjoin(og_core_package_path, 'opengever')
    exp_script_with_checksum = re.compile(
        r'<script\s*tal:attributes="src string:\${here/portal_url}/\+\+resource\+\+(?P<resource>.*)/(?P<filename>.*\.js)\?_v=(?P<checksum>.*)\s*"')
    exp_script_without_checksum = re.compile(
        r'<script\s*tal:attributes="src string:\${here/portal_url}/(?P<resource_id>\+\+resource\+\+.*/.*\.js)\s*"')

    def md5(self, file_path):
        """Return an md5 checksum for the file at file_path."""

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def zope_page_template_paths(self):
        for root, dirnames, filenames in os.walk(self.og_namespace_path):
            for filename in fnmatch.filter(filenames, '*.pt'):
                yield pjoin(root, filename)

    def find_scripts_with_checksum_query_parameter(self):
        for template_path in self.zope_page_template_paths():
            with open(template_path, 'r') as template_file:
                match = self.exp_script_with_checksum.search(
                    template_file.read())
                if match:
                    yield(template_path, match)

    def find_scripts_without_checksum_query_parameter(self):
        for template_path in self.zope_page_template_paths():
            with open(template_path, 'r') as template_file:
                match = self.exp_script_without_checksum.search(
                    template_file.read())
                if match:
                    yield(template_path, match)

    def format_resource_name(self, template_path, resource_id):
        """Return an unique resource name for template_path and resource_id."""

        relative_path = relpath(template_path, start=self.og_core_package_path)
        return "{}:{}".format(relative_path, resource_id)

    def test_manually_included_js_files_have_cache_invalidation(self):
        missing = []
        for template_path, match in self.find_scripts_without_checksum_query_parameter():
            resource_id = match.group('resource_id')
            missing.append(self.format_resource_name(template_path, resource_id))
        if missing:
            self.fail(
                'The following javascript includes are missing a cache '
                'invalidation query string parameter. Please append '
                '"?_v=[checksum]" to the "src" url.\n\n{}'.format(
                    pprint.pformat(missing)))

    def test_js_cache_invalidation_parameters_are_updated_in_templates(self):
        current_checksums = {}
        expected_checksums = {}

        for template_path, match in self.find_scripts_with_checksum_query_parameter():
            resource = match.group('resource')
            js_filename = match.group('filename')
            current_checksum = match.group('checksum')

            segments = self.resource_dir_to_path_segments.get(resource)
            if not segments:
                segments = tuple(resource.split('.')) + ('browser', 'resources',)
            full_segments = (self.og_core_package_path,) + segments + (js_filename,)
            js_file_path = pjoin(*full_segments)
            expected_checksum = self.md5(js_file_path)

            resource_id = "++resource++{}/{}".format(resource, js_filename)
            key = self.format_resource_name(template_path, resource_id)
            # Only populate the dict when the checksums are different, this
            # results in better exception failure output. Otherwise correct
            # checksums are listed as context which is a bit confusing.
            if current_checksum != expected_checksum:
                current_checksums[key] = current_checksum
                expected_checksums[key] = expected_checksum

        self.assertDictEqual(
            current_checksums,
            expected_checksums,
            '\n\nError: You seem to have modified a javascript file without '
            'updating the cache invalidation version parameter. You most '
            'likely should update the template with the new checksum (see '
            'diff above).')
