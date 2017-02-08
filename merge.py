import pkg_resources
import sys

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use: ./bin/zopepy ./src/profile-merge-tool/merge.py'
    sys.exit(1)


from path import Path
import os


def step(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print '🔧 ', message
            try:
                returnvalue = func(*args, **kwargs)
            except:
                print '💥'
                raise
            else:
                print '✔ 🍺'
                print ''
                return returnvalue
        return wrapper
    return decorator


class MergeTool(object):

    def __init__(self):
        self.here_dir = Path(__file__).parent.abspath()
        self.buildout_dir = Path(__file__).parent.parent.parent.abspath()
        assert self.buildout_dir.joinpath('bootstrap.py'), \
            'Could not find buildout root.'

    def __call__(self):
        self.create_opengever_core_profile()

    @step('Create opengever.core Generic Setup profile.')
    def create_opengever_core_profile(self):
        source = self.here_dir.joinpath('opengever-core')
        target = self.buildout_dir.joinpath('opengever', 'core')
        cmd = 'cp -r {}/* {}'.format(source, target)
        print '>', cmd
        os.system(cmd)


if __name__ == '__main__':
    MergeTool()()
