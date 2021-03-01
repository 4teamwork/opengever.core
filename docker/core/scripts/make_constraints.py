# Usage: bin/zopepy ./docker/scripts/make_constraints.py >./docker/versions.txt

from zc.buildout.buildout import Buildout
import os


def get_versions(buildout):
    for version in buildout['versions'].items():
        yield '=='.join(version)


if __name__ == '__main__':

    buildout_dir = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    config_file = os.path.join(buildout_dir, 'versions.cfg')

    buildout = Buildout(
        config_file=config_file,
        cloptions=[('buildout', 'directory', '/tmp')],
        user_defaults=False,
    )

    print('\n'.join(sorted(get_versions(buildout))))
