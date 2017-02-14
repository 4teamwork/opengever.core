import pkg_resources
import sys

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use: ./bin/zopepy ./src/profile-merge-tool/dump-differ.py ./src/profile-merge-tool/dumps/before ./src/profile-merge-tool/dumps/after'
    sys.exit(1)


from path import Path
import os


class Differ(object):

    def __call__(self, first_dir, second_dir):
        self.first_dir = first_dir
        self.second_dir = second_dir
        self.compare_filelist()
        if not self.get_differing_files():
            print 'No changes.'
        else:
            print 'Differences found:'
            self.cli()

    def cli(self):
        while True:
            diffcmd = 'vimdiff'
            print ''
            for num, name in self.numbered_files():
                print '-', num, name
            print '- d change diffcommand ({!r})'.format(diffcmd)

            input = raw_input('Diff number: ').strip()
            if input.strip() == 'd':
                diffcmd = raw_input('Diff command: ').strip()
                continue

            try:
                name = dict(self.numbered_files())[int(input)]
            except (ValueError, KeyError):
                print 'Error: bad input'
                continue

            cmd = diffcmd + ' {} {}'.format(
                self.first_dir.joinpath(name),
                self.second_dir.joinpath(name))
            print '>', cmd
            os.system(cmd)

    def numbered_files(self):
        return enumerate(self.get_differing_files())

    def get_differing_files(self):
        result = []
        for relpath in self.files(self.first_dir, relative=True):
            first = self.first_dir.joinpath(relpath)
            second = self.second_dir.joinpath(relpath)
            if first.bytes() != second.bytes():
                result.append(relpath)

        return result

    def compare_filelist(self):
        first_files = self.files(self.first_dir, relative=True)
        second_files = self.files(self.second_dir, relative=True)
        added = sorted(set(second_files) - set(first_files))
        removed = sorted(set(first_files) - set(second_files))
        assert not added, 'Unexpectedly added files: {!r}'.format(added)
        assert not removed, 'Unexpectedly added files: {!r}'.format(removed)

    def files(self, folder, relative=False):
        files = folder.walkfiles()
        files = filter(lambda path: not path.startswith(folder.joinpath('structure')),
                       files)
        if relative:
            return map(lambda path: path.relpath(folder), files)
        else:
            return files



if __name__ == '__main__':
    _, first_dir, second_dir = map(Path, sys.argv)
    Differ()(first_dir, second_dir)
