from opengever.testing import IntegrationTestCase
from operator import itemgetter
from path import Path
import hashlib
import os.path
import re


class TestDumpFixtureStructureToReadme(IntegrationTestCase):

    def test_dump_fixure(self):
        """This test dumps the fixture structure into the readme for
        documentation purposes.
        It also will fail every time it changes the readme,
        so that we can detect fixture changes without readme update in
        pull requests.
        """
        data = {'user': {}, 'object': {}, 'raw': {}}
        for name, (type_, value) in self.layer['fixture_lookup_table'].items():
            data[type_][name] = value

        md5_before = self._readme_md5()

        self._update_in_readme(
            'users',
            '\n'.join(
                ['- ``self.{}``: ``{}``'.format(name, userid)
                 for name, userid in sorted(data['user'].items())]))

        self._update_in_readme(
            'raw',
            '\n'.join(
                ['- ``self.{}``: ``{}``'.format(name, userid)
                 for name, userid in sorted(data['raw'].items())]))

        self._update_in_readme(
            'objects',
            '.. code::\n\n' + '\n'.join(
                self._render_tree(self._build_tree(data['object']),
                                  level=1)))

        md5_after = self._readme_md5()
        self.assertEquals(
            md5_before, md5_after,
            'Fixture has changed and readme was not updated.\n'
            'run:\n'
            ' $ bin/test -t TestDumpFixtureStructureToReadme\n'
            'then commit the changes in the README.rst.')

    def _build_tree(self, name_to_path):
        nodes_by_path = {path: {'name': name, 'children': []}
                         for name, path in name_to_path.items()}
        root_nodes = []
        for path, node in nodes_by_path.items():
            parent_path = os.path.dirname(path)
            if parent_path in nodes_by_path:
                nodes_by_path[parent_path]['children'].append(node)
            else:
                root_nodes.append(node)
        return root_nodes

    def _render_tree(self, nodes, level=0):
        lines = []
        indent = ' ' * 2 * level
        for node in sorted(nodes, key=itemgetter('name')):
            lines.append('{}- self.{}'.format(indent, node['name']))
            lines.extend(self._render_tree(node['children'], level=level+1))
        return lines

    def _update_in_readme(self, name, text):
        buildout_dir = Path(__file__).joinpath('..', '..', '..', '..').abspath()
        readme_file = buildout_dir.joinpath('README.rst')
        readme = readme_file.bytes()
        match = re.search('(<fixture:{0}>).*?(.. </fixture:{0}>)'.format(name),
                          readme, re.DOTALL)
        text = match.group(1) + '\n\n' + text.strip() + '\n\n' + match.group(2).strip()
        readme = readme[:match.start()] + text + readme[match.end():]
        readme_file.write_bytes(readme)

    def _readme_md5(self):
        buildout_dir = Path(__file__).joinpath('..', '..', '..', '..').abspath()
        readme_file = buildout_dir.joinpath('README.rst')
        hash_md5 = hashlib.md5()
        with readme_file.open('rb') as fio:
            for chunk in iter(lambda: fio.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
