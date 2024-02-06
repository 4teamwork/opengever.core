from unittest import TestCase
from zc.buildout.buildout import Buildout
import glob
import os.path


EXCLUDED_PACKAGES = set([
    'cryptography',  # On CentOS 7 we need an older version because of an old OpenSSL version
])


class TestVersionPinnings(TestCase):

    def test_buildout_and_docker_versions_are_equal(self):
        buildout_versions = self.get_buildout_versions()
        docker_versions = self.get_docker_versions()

        common_packages = set(buildout_versions.keys()) & set(docker_versions.keys())
        common_packages -= EXCLUDED_PACKAGES
        for package in common_packages:
            self.assertEqual(
                buildout_versions[package],
                docker_versions[package],
                'Different pinnings for {}.'.format(package),
            )

    def get_buildout_versions(self):
        versions_cfg = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))), 'versions.cfg')
        buildout = Buildout(
            config_file=versions_cfg,
            cloptions=[('buildout', 'directory', '/tmp')],
            user_defaults=False,
        )
        return buildout['versions']

    def get_docker_versions(self):
        requirements_dir = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__)))), 'docker', 'core')
        requirements_files = glob.glob(requirements_dir + '/requirements*.txt')
        versions = {}
        for requirements_file in requirements_files:
            with open(os.path.join(requirements_file), 'r') as rfile:
                for line in rfile:
                    try:
                        name, version = line.split('==')
                    except ValueError:
                        continue
                    else:
                        versions[name] = version.strip()

        return versions
