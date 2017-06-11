from datetime import datetime
from fnmatch import fnmatch
from os import listdir
from os.path import basename
from os.path import isdir
from os.path import islink
from os.path import join as pjoin
from plone.i18n.normalizer.de import normalizer
from uuid import uuid4
import argparse
import errno
import json
import os


DEFAULT_RESPONSIBLE = 'lukas.graf'
DEFAULT_USERS_GROUP = 'og_demo-ftw_users'

# List of fnmatch() patterns to specify which "documents" to ignore
IGNORES = ['*.DS_Store']


class FilesystemWalker(object):

    def __init__(self, top, followlinks=False,
                 repo_depth=3, users_group=DEFAULT_USERS_GROUP):
        self.top = top
        self.followlinks = followlinks
        self.repo_depth = repo_depth
        self.users_group = users_group

    def __iter__(self):
        return self.walk(
            self.top, followlinks=self.followlinks, repo_depth=self.repo_depth)

    def make_guid(self, path):
        """Create a unique, but human readable GUID, like
        '/Geographie/Geographie nach Fachgebiet-a459ba73'
        """
        # Transliterate Umlauts to ae, oe, ue, after that safe-encode to ASCII
        normalized_path = normalizer.normalize(
            path.decode('utf-8')).encode('ascii', errors='replace')
        common_path_prefix = self.top.rstrip(os.path.sep)
        rel_path = normalized_path.replace(common_path_prefix, '', 1)
        suffix = uuid4().hex[:8]
        guid = '/%s-%s' % (rel_path.lstrip('/'), suffix)
        return guid

    def walk(self, top, followlinks=False, level=0,
             parent_guid=None, repo_depth=3):
        """Custom implementation of os.walk that keeps track of nesting level.
        """
        names = listdir(top)

        # Folderish item
        container = {
            'path': top,
            'guid': self.make_guid(top),
            'parent_guid': parent_guid,
            'title': basename(top.rstrip(os.path.sep)),
        }

        if level == 0:
            container['type'] = 'reporoot'
            container.pop('parent_guid')
            container['review_state'] = 'repositoryroot-state-active'
            container['title_de'] = container.pop('title')
            container['_permissions'] = {
                'read': [self.users_group],
                'add': [self.users_group],
                'edit': [self.users_group],
                'close': [],
                'reactivate': [],
            }

        elif level <= repo_depth:
            container['type'] = 'repofolder'
            container['review_state'] = 'repositoryfolder-state-active'
            container['title_de'] = container.pop('title')

        elif level > repo_depth:
            container['type'] = 'dossier'
            container['responsible'] = DEFAULT_RESPONSIBLE
            container['review_state'] = 'dossier-state-active'

        yield container

        dirs = []
        for name in names:
            path = pjoin(top, name)
            if isdir(path):
                dirs.append(name)
            else:
                # TODO: Ignore IGNORES
                if any(fnmatch(name, pattern) for pattern in IGNORES):
                    print("Ignoring %s" % name)
                    continue

                # Non-folderish item (i.e. document)
                item = {
                    'path': path,
                    'guid': self.make_guid(path),
                    'parent_guid': container['guid'],
                    'title': basename(name),
                    'type': 'document',
                    'review_state': 'document-state-draft',
                    'filepath': path,
                }
                yield item

        for name in dirs:
            new_path = pjoin(top, name)
            if followlinks or not islink(new_path):
                for node in self.walk(
                        new_path, followlinks, level=level + 1,
                        parent_guid=container['guid'], repo_depth=repo_depth):
                    yield node


class BundleFactory(object):

    def __init__(self, args):
        self.args = args
        self.source_dir = args.source_dir
        self.target_dir = args.target_dir
        self.repo_nesting_depth = args.repo_nesting_depth
        self.users_group = args.users_group

        self.repofolder_paths = []
        self.items = []

    @property
    def bundle_name(self):
        ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        return 'Sample-%s.oggbundle' % ts

    def dump_bundle(self):
        bundle_dir = pjoin(self.target_dir, self.bundle_name)
        os.makedirs(bundle_dir)
        print("Created %s" % bundle_dir)

        items = {
            'reporoot': [],
            'repofolder': [],
            'dossier': [],
            'document': [],
        }

        walker = FilesystemWalker(self.source_dir, followlinks=True,
                                  repo_depth=self.repo_nesting_depth,
                                  users_group=self.users_group)
        for item in walker:
            items[item['type']].append(item)

            # Strip keys not allowed in OGGBundle items
            for key in ('type', 'path'):
                item.pop(key)

        self.dump_items(items, bundle_dir)

    def dump_items(self, items, bundle_dir):
        for key, itemlist in items.iteritems():
            json_fn = '%ss.json' % key
            json_file_path = pjoin(bundle_dir, json_fn)
            with open(json_file_path, 'w') as json_file:
                json.dump(itemlist, json_file, sort_keys=True,
                          indent=4, separators=(',', ': '))


def get_var_dir():
    var = pjoin(os.getcwd(), 'var')
    if os.path.isdir(var):
        return var


def parse_args():
    parser = argparse.ArgumentParser(
        description='Create OGGBundle from directory structure')
    parser.add_argument(
        'source_dir',
        help='Source directory')
    parser.add_argument(
        'target_dir', nargs='?',
        help='Target directory where bundle will be created')

    parser.add_argument(
        '--repo-nesting-depth', type=int, default=3,
        help='Repository nesting depth')

    parser.add_argument(
        '--users-group', type=str,
        help='Users group to grant local roles on reporoot to',
        required=True)

    args = parser.parse_args()

    if args.target_dir is None:
        var_dir = get_var_dir()
        if var_dir is None:
            raise parser.error(
                "Couldn't automatically determine var/ directory, please "
                "specify 'target_dir' manually.")
        target_dir = pjoin(var_dir, 'bundles')
        mkdir_p(target_dir)
        args.target_dir = target_dir
    return args


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def main():
    args = parse_args()
    factory = BundleFactory(args)
    factory.dump_bundle()
