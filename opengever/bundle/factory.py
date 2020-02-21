from collections import namedtuple
from datetime import datetime
from datetime import date
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
import platform


# List of fnmatch() patterns to specify which "documents" to ignore
IGNORES = ['*.DS_Store', '*.dll', '*.exe']


DirectoryNode = namedtuple('Node', ['path', 'guid', 'parent_guid', 'level'])
FileNode = namedtuple('Node', ['path', 'guid', 'parent_guid'])


def creation_date(path_to_file):
    """
    From https://stackoverflow.com/questions/237079
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


class FilesystemWalker(object):

    def __init__(self, top, followlinks=False, skip_top=False):
        self.top = top
        self.followlinks = followlinks
        self.skip_top = skip_top

    def __iter__(self):
        return self.walk(
            self.top, followlinks=self.followlinks, skip_container=self.skip_top)

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
             parent_guid=None, skip_container=False):
        """Custom implementation of os.walk that keeps track of nesting level.
        """
        names = listdir(top)

        # Folderish item
        if not skip_container:
            container = DirectoryNode(path=top,
                                      guid=self.make_guid(top),
                                      parent_guid=parent_guid,
                                      level=level)
            yield container
            level += 1
        else:
            container = None

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
                node = FileNode(path=path,
                                guid=self.make_guid(path),
                                parent_guid=getattr(container, "guid", None))
                yield node

        for name in dirs:
            new_path = pjoin(top, name)
            if followlinks or not islink(new_path):
                for node in self.walk(
                        new_path, followlinks, level=level,
                        parent_guid=getattr(container, "guid", None)):
                    yield node


class OGGBundleItemCreator(object):

    def __init__(self, responsible, repo_depth=-1, user_group=None, import_reference=None, content_only=False):
        self.repo_depth = repo_depth
        self.responsible = responsible
        self.user_group = user_group
        self.import_reference = import_reference
        self.content_only = content_only

    def __call__(self, node):
        if not self.isdir(node):
            return OGGBundleDocument(node)
        elif node.level == 0:
            if not self.content_only:
                return OGGBundleRepoRoot(node, self.user_group)
            else:
                return OGGBundleDossier(node, self.responsible, self.import_reference)
        elif node.level <= self.repo_depth and not self.content_only:
            return OGGBundleRepoFolder(node)
        else:
            return OGGBundleDossier(node, self.responsible)

    @staticmethod
    def isdir(node):
        return isinstance(node, DirectoryNode)


class OGGBundleItemBase(object):

    item_type = None
    review_state = None

    def __init__(self, node):
        self.node = node
        self.path = node.path
        self._data = {
            'guid': node.guid,
            'review_state': self.review_state,
            'title': self.title
            }

    def as_dict(self):
        return self._data

    @property
    def title(self):
        return basename(self.path.rstrip(os.path.sep))


class OGGBundleRepoRoot(OGGBundleItemBase):

    item_type = 'reporoot'
    review_state = 'repositoryroot-state-active'

    def __init__(self, node, users_group):
        super(OGGBundleRepoRoot, self).__init__(node)
        self._data['title_de'] = self._data.pop('title')
        self._data['_permissions'] = {
                'read': [users_group],
                'add': [users_group],
                'edit': [users_group],
                'close': [],
                'reactivate': [],
            }


class OGGBundleRepoFolder(OGGBundleItemBase):

    item_type = 'repofolder'
    review_state = 'repositoryfolder-state-active'

    def __init__(self, node):
        super(OGGBundleRepoFolder, self).__init__(node)
        self._data['title_de'] = self._data.pop('title')
        self._data['parent_guid'] = self.node.parent_guid


class OGGBundleDossier(OGGBundleItemBase):

    item_type = 'dossier'
    review_state = 'dossier-state-active'

    def __init__(self, node, responsible, parent_reference=None):
        super(OGGBundleDossier, self).__init__(node)
        self._data['parent_guid'] = self.node.parent_guid
        self._data['responsible'] = responsible
        if parent_reference is not None:
            self._data['parent_reference'] = parent_reference


class OGGBundleDocument(OGGBundleItemBase):

    item_type = 'document'
    review_state = 'document-state-draft'

    def __init__(self, node):
        super(OGGBundleDocument, self).__init__(node)
        self._data['parent_guid'] = self.node.parent_guid
        self._data['filepath'] = self.node.path
        self._data['document_date'] = self.creation_date
        self._data['changed'] = self.modification_date

    @property
    def modification_date(self):
        return datetime.fromtimestamp(os.path.getmtime(self.path)).isoformat()

    @property
    def creation_date(self):
        return date.fromtimestamp(creation_date(self.path)).isoformat()


class BundleFactory(object):

    def __init__(self, args):
        self.args = args
        self.source_dir = args.source_dir
        self.target_dir = args.target_dir
        self.repo_nesting_depth = args.repo_nesting_depth
        self.users_group = args.users_group
        self.dossier_responsible = args.dossier_responsible

        self.import_reference = []
        if args.import_repository_reference is not None:
            self.import_reference.append(args.import_repository_reference)
        if args.import_dossier_reference is not None:
            self.import_reference.append(args.import_dossier_reference)

        # When repo_nesting_depth is set to -1, we create a partial bundle with
        # only content (no reporoot and repofolder). In that case we also skip
        # the root dossier (we do not include it as a dossier in the bundle)
        self.partial_bundle = self.repo_nesting_depth == -1

        self.repofolder_paths = []
        self.items = []

        self.item_creator = OGGBundleItemCreator(
            self.dossier_responsible,
            repo_depth=self.repo_nesting_depth,
            user_group=self.users_group,
            import_reference=self.import_reference,
            content_only=self.partial_bundle)

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

        walker = FilesystemWalker(self.source_dir,
                                  followlinks=True,
                                  skip_top=self.partial_bundle)
        for node in walker:
            item = self.item_creator(node)
            items[item.item_type].append(item.as_dict())

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


def get_parser():
    parser = argparse.ArgumentParser(
        description='Create OGGBundle from directory structure')
    parser.add_argument(
        'source_dir',
        help='Source directory')
    parser.add_argument(
        'target_dir', nargs='?',
        help='Target directory where bundle will be created')

    parser.add_argument(
        '--repo-nesting-depth', type=int, default=-1,
        help='Repository nesting depth. If not set, no repository tree will be'
        ' generated by the factory, only content items (dossiers, mails and'
        ' documents).')

    parser.add_argument(
        '--import-repository-reference', type=int, nargs="*",
        help='Reference position of repository into which this bundle will be '
             'imported, in the form of space separated integers. For example\n'
             '--import-repository-reference 1 3 5 corresponds to repository '
             'with reference number 1.3.5')

    parser.add_argument(
        '--import-dossier-reference', type=int, nargs="*",
        help='Reference position of dossier into which this bundle will be '
             'imported, in the form of space separated integers.'
             '--import-repository-reference has to be specified in order '
             'to specify --import-dossier-reference. For example\n'
             '--import-repository-reference 1 3 5 --import-dossier-reference 472 9\n'
             'corresponds to subdossier with reference number 1.3.5 / 472.9'
             '(Position 1.3.5, Dossier 472, Subdossier 9)')

    parser.add_argument(
        '--users-group', type=str,
        help='Users group to grant local roles on reporoot to')

    parser.add_argument(
        '--dossier-responsible', type=str,
        help='User used as responsible for all dossiers',
        required=True)

    return parser


def parse_args():
    parser = get_parser()

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

    if args.repo_nesting_depth == -1 and args.import_repository_reference is None:
        raise parser.error(
            "When generating a partial bundle (repo-nesting-dept = -1), "
            "a position into which the bundle will be imported has "
            "to be specified")

    if args.repo_nesting_depth != -1 and args.import_repository_reference is not None:
        raise parser.error(
            "Partial bundles can only contain contentish items, not "
            "repository folders or roots.")

    if args.import_dossier_reference is not None and args.import_repository_reference is None:
        raise parser.error(
            "Can only specify import-dossier-reference if "
            "import-repository-reference has been specified")

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
