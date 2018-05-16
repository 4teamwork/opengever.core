from ftw.testing.genericsetup import apply_generic_setup_layer
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from unittest2 import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstall(TestCase, GenericSetupUninstallMixin):

    package = 'plonetheme.teamraum'
    is_product = True
    skip_files = (
        'mimetypes.xml',  # Because the order of the installed mimetypes may be different in the before and after run.
        'viewlets.xml',  # We're currently unable to revert this configuration.
    )

    def assertSnapshotsEqual(self, before_id='before-install',
                             after_id='after-uninstall', msg=None):
        """Assert that two configuration snapshots are equal.

        Compare setup-tool snapshots identified by ``before_id`` and
        ``after_id`` and assert that they are equal.

        This method is overridden for the following reason:
        Programatically setting the value of an app registry value to an
        empty string will result in "<value></value>" in the after run.
        But the before run creates "<value/>" which will make the tests fail.
        That's why we're going to manually strip these line from the original
        diff.

        """
        before = self.setup_tool._getImportContext('snapshot-' + before_id)
        after = self.setup_tool._getImportContext('snapshot-' + after_id)

        diff = self.setup_tool.compareConfigurations(
            before, after, skip=self.skip_files
        )

        diff_list = [line for line in diff.split('\n')
                     if not line.startswith(('+++', '---'))
                     and line.startswith(('+', '-'))]

        lines_to_be_removed = []
        for index, line in enumerate(diff_list):
            if line.startswith('-') and '<value/>' in line and diff_list[index+1].startswith('+') and '<value></value>' in diff_list[index+1]:
                lines_to_be_removed.extend([index, index+1])

        for i in sorted(lines_to_be_removed, reverse=True):
            diff_list.pop(i)

        self.maxDiff = None
        self.assertEquals(
            diff_list,
            [],
            msg='{0}\n\nOriginal diff:\n\n{1}'.format(msg, diff))
