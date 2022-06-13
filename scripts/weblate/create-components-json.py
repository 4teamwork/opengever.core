"""
This script creates the necessary JSON files to use Weblate's `import_json`
management command to import all the opengever.* packages as components in
a Weblate OneGov GEVER Project.

Usage:

# python create-component-import-json.py <https_repo_url_including_token>

Then import the two generated JSON files (main_component.json and
components.json) into Weblate using the "python manage.py import_json"
command-line given at the end of this script.
"""

from urlparse import urlparse
from urlparse import urlunparse
import fnmatch
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap


logging.basicConfig(level=logging.INFO, format='')
log = logging.getLogger()


repository_url = sys.argv[1]


class Repository(object):

    def __init__(self, full_url):
        self._tempdir = None
        self.checkout_path = None

        if not full_url.startswith('https://'):
            raise NotImplementedError(
                "Only HTTPS repository URLs are suppported")

        self._full_url = full_url

    def __enter__(self):
        """Clone the repo to a temporary directory.
        """
        self._tempdir = tempfile.mkdtemp(prefix='create-components-')
        self.checkout_path = '%s/checkout' % self._tempdir
        print "Cloning %s to %s" % (self._full_url, self.checkout_path)
        cmd = 'git clone %s %s' % (self._full_url, self.checkout_path)
        # XXX: Avoid shell=True
        output = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        print output
        return self

    def __exit__(self, type, value, tb):
        """Remove the temporary directory containing the repo clone.
        """
        print "Removing %s" % self._tempdir
        shutil.rmtree(self._tempdir)

    @property
    def url_with_token(self):
        return self._full_url

    @property
    def url(self):
        u = urlparse(self._full_url)
        if 'github.com' not in u.netloc:
            raise NotImplementedError('Only github URLs are supported')

        return urlunparse(
            (u.scheme, 'github.com', u.path, u.params, u.query, u.fragment))

    @property
    def browser_url_pattern(self):
        base_url = self.url.replace('.git', '')
        return base_url + '/blob/%(branch)s/%(file)s#L%(line)s'


class PotFile(object):

    def __init__(self, repo, path):
        self.path = path
        self.repo = repo

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def relative_path(self):
        return self.path.replace(self.repo.checkout_path, '', 1)

    @property
    def package(self):
        return Package.from_pot_filename(self.filename)

    @property
    def ignored(self):
        if not self.filename.startswith('opengever'):
            # Skip non-opengever po[t] files
            return True

        if self.filename.endswith('-manual.pot'):
            # -manual.pot files aren't supported yet
            return True

        return False

    def assert_expected_path_structure(self):
        pkg = self.package
        expected_path = '/%s/locales/%s' % (pkg.slashed, self.filename)
        try:
            assert self.relative_path == expected_path
        except AssertionError:
            msg = """
            Path for file %r doesn't match expected structure!
              Actual path:   %s
              Expected path: %s
            """ % (self.filename, self.relative_path, expected_path)
            log.error(textwrap.dedent(msg))
            raise


class Package(object):

    def __init__(self, parts):
        self.parts = parts

    @classmethod
    def from_pot_filename(cls, filename):
        """Alternative constructor to create a Package based on a .pot name.
        """
        parts = filename.split('.')[:-1]
        return cls(parts)

    @property
    def dotted(self):
        """Dotted representation for a Package.
        Example: opengever.ogds.base
        """
        return '.'.join(self.parts)

    @property
    def slashed(self):
        """Slash separated representation for a Package.
        Example: opengever/ogds/base
        """
        return '/'.join(self.parts)

    @property
    def slug(self):
        """Weblate compatible slug representation for a Package.
        Example: opengever-ogds-base
        """
        return '-'.join(self.parts)

    def __repr__(self):
        """String representation for a Package
        """
        return '<Package %s>' % self.dotted

    def __lt__(self, other):
        """Sort packages by comparing dotted names
        """
        return self.dotted < other.dotted


def find_pkgs_with_pot_files(repo):
    search_path = os.path.join(repo.checkout_path, 'opengever')

    packages = []
    for root, dirnames, filenames in os.walk(search_path):
        for filename in fnmatch.filter(filenames, '*.pot'):
            path = os.path.join(root, filename)
            pot_file = PotFile(repo, path)

            if pot_file.ignored:
                continue

            pot_file.assert_expected_path_structure()

            packages.append(pot_file.package)
    return packages


def build_component(repo, pkg, vcs=True):
    name = pkg.dotted
    slug = pkg.slug
    filemask = '%s/locales/*/LC_MESSAGES/%s.po' % (pkg.slashed, pkg.dotted)
    german_po = '%s/locales/de/LC_MESSAGES/%s.po' % (pkg.slashed, pkg.dotted)
    # pot_path = '%s/locales/%s.pot' % (pkg.slashed, pkg.dotted)

    component = {
        "name": name,
        "slug": slug,
        "vcs": "git",
        "repo": repo.url_with_token,
        "push": repo.url_with_token,
        "repoweb": repo.browser_url_pattern,
        "branch": "master",
        "merge_style": "rebase",
        "filemask": filemask,
        "template": german_po,
        # "new_base": pot_path,
        "new_lang": "none",
        "file_format": "po-mono",
    }

    if not vcs:
        del component['vcs']
        del component['repo']
        del component['push']
        del component['repoweb']

    return component


def pretty_json(data):
    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))


def create_components(repo):
    components = []
    packages = sorted(find_pkgs_with_pot_files(repo))
    for idx, pkg in enumerate(packages):
        if idx == 0:
            # Main component
            main_component = build_component(repo, pkg)
            main_component_name = pkg.slug
            log.info('Main component: %s' % main_component_name)
        else:
            component = build_component(repo, pkg, vcs=False)
            components.append(component)

    with open('main_component.json', 'w') as main_component_json:
        main_component_json.write(pretty_json([main_component]))
        log.info('Wrote main_component.json')

    with open('components.json', 'w') as components_json:
        components_json.write(pretty_json(components))
        log.info('Wrote components.json')

    log.info('\nNow run the following to import your components:\n'
             'PROJ="<your_project_slug>" && python manage.py import_json '
             '--project ${PROJ} main_component.json && python manage.py '
             'import_json --project ${PROJ} --main-component %s '
             'components.json' % main_component_name)


def main():
    with Repository(repository_url) as repo:
        create_components(repo)


if __name__ == '__main__':
    main()
