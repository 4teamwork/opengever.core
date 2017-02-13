import pkg_resources
import sys

USAGE = './bin/instance run ./src/profile-merge-tool/dump-gs-profile.py [NAME]'
try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use:' + USAGE
    sys.exit(1)


from opengever.maintenance.debughelpers import setup_app
from opengever.maintenance.debughelpers import setup_option_parser
from opengever.maintenance.debughelpers import setup_plone
from path import Path
from StringIO import StringIO
from tarfile import TarFile


BUILDOUT_DIR = Path(__file__).joinpath('..', '..', '..', '..').abspath()
assert BUILDOUT_DIR.joinpath('bootstrap.py').isfile(), \
    'No bootstrap.py in {}'.format(BUILDOUT_DIR)
DUMPS_DIR = BUILDOUT_DIR.joinpath('src', 'profile-merge-tool', 'dumps')


def main():
    app = setup_app()
    parser = setup_option_parser()
    options, args = parser.parse_args()
    if len(args) != 1:
        print 'ERROR, use:' + USAGE
        sys.exit(1)

    target_dir = DUMPS_DIR.joinpath(args[0])
    if target_dir.exists():
        print 'WARNING: {} exists'.format(target_dir)
        raw_input('DELETE by pressing enter (Ctrl-C to abort): ')
        target_dir.rmtree()

    plone = setup_plone(app, options)
    portal_setup = plone.portal_setup

    blacklist = (
        # vs.genericsetup.ldap does not encode properly and crashes
        # the export. I assume that a lot would not work when LDAP wasn't
        # installed, so it is safe to blacklist it for the diff.
        'ldap-settings-export',
    )
    steps = [step for step in portal_setup.listExportSteps()
             if step not in blacklist]
    result = portal_setup._doRunExportSteps(steps)
    tar = TarFile.open(fileobj=StringIO(result['tarball']), mode='r:gz')
    tar.extractall(target_dir)


if __name__ == '__main__':
    main()
