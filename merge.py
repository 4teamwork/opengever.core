import pkg_resources
import sys

try:
    pkg_resources.get_distribution('Products.CMFPlone')
except pkg_resources.DistributionNotFound:
    print 'ERROR, use: ./bin/zopepy ./src/profile-merge-tool/merge.py'
    sys.exit(1)


from lxml import etree
from operator import methodcaller
from path import Path
from plone.memoize import instance
from pprint import pprint
import os
import re


def step(message):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return execute_step(message, func, *args, **kwargs)
        return wrapper
    return decorator


def execute_step(message, func, *args, **kwargs):
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


class MergeTool(object):

    def __init__(self):
        self.here_dir = Path(__file__).parent.abspath()
        self.buildout_dir = Path(__file__).parent.parent.parent.abspath()
        assert self.buildout_dir.joinpath('bootstrap.py'), \
            'Could not find buildout root.'
        self.opengever_dir = self.buildout_dir.joinpath('opengever')
        self.og_core_profile_dir = self.opengever_dir.joinpath(
            'core', 'profiles', 'default')

    def __call__(self):
        self.create_opengever_core_profile()
        self.list_old_profiles()
        self.migrate_dependencies()
        self.migrate_standard_xmls()
        self.migrate_mailhost()
        self.validate_no_leftovers()

    @step('Create opengever.core Generic Setup profile.')
    def create_opengever_core_profile(self):
        source = self.here_dir.joinpath('opengever-core')
        target = self.opengever_dir.joinpath('core')
        cmd = 'cp -r {}/* {}'.format(source, target)
        print '   >', cmd
        os.system(cmd)

    @step('These profiles will be merged in this order:')
    def list_old_profiles(self):
        for profile in self.profiles_to_migrate:
            print '  ', profile

    @step('Migrate GS dependencies into opengever.core profile.')
    def migrate_dependencies(self):
        # Migrate dependencies according to recursive dependency lookup,
        # skipping merged profiles.
        # We do not remove dependencies from old profiles since we will
        # no longer install them and we need the dependencies for upgrade
        # step ordering.
        target_metadata = self.og_core_profile_dir.joinpath('metadata.xml')
        with target_metadata.open() as fio:
            target_doc = etree.parse(fio)

        dependencies_node = target_doc.xpath('//dependencies')[0]
        dependencies_node.text = '\n' + ' ' * 8
        for profile in self.read_dependencies('opengever.policy.base:default'):
            if profile in self.profiles_to_migrate:
                # do not migrate dependency to migrated profiles (og.task, ..)
                continue
            node = etree.SubElement(dependencies_node, 'dependency')
            node.text = profile
            node.tail = dependencies_node.text

        node.tail = '\n' + ' ' * 4
        target_metadata.write_bytes(etree.tostring(target_doc))

    def migrate_standard_xmls(self):
        standard_xmls = (
            'actions.xml',
            'browserlayer.xml',
            'catalog.xml',
            'controlpanel.xml',
            'jsregistry.xml',
            'properties.xml',
            'propertiestool.xml',
            'registry.xml',
            'rolemap.xml',
            'skins.xml',
            'viewlets.xml',
        )

        map(lambda name: execute_step(
            'Migrating {}'.format(name), self.standard_migrate_xml, name),
            standard_xmls)

    @step('Migrate mailhost.xml')
    def migrate_mailhost(self):
        # There is only one mailhost.xml.
        # Since everything is in the XML roo tnode, we cannot use
        # standard_migrate_xml.
        xmls = self.find_file_in_profiles_to_migrate('mailhost.xml')
        assert len(xmls) == 1, 'Expected exactly 1 mailhost.xml, got {!r}'.format(
            xmls)
        xmls[0].move(self.og_core_profile_dir)

    @step('Analyze')
    def validate_no_leftovers(self):
        errors = False

        for profile in self.profiles_to_migrate:
            for item in self.profile_path(profile).listdir():
                if item.name == 'metadata.xml':
                    continue
                if not errors:
                    print '   ERROR: leftovers found:'
                    errors = True

                print '  ', profile.ljust(35), item.isdir() and 'D' or ' ', item.name

        assert not errors, 'Should not have any leftovers'

    def standard_migrate_xml(self, filename):
        with self.og_core_profile_dir.joinpath(filename).open() as fio:
            target = etree.parse(fio)

        for path in self.find_file_in_profiles_to_migrate(filename):
            with path.open() as fio:
                doc = etree.parse(fio)

            if target.getroot().getchildren():
                target.getroot().getchildren()[-1].tail = '\n\n\n    '
            else:
                target.getroot().text = '\n\n    '

            comment = etree.Comment('merged from {}'.format(
                path.relpath(self.buildout_dir)))
            comment.tail = '\n    '
            target.getroot().append(comment)

            map(target.getroot().append, doc.getroot().getchildren())
            path.unlink()

        self.og_core_profile_dir.joinpath(filename).write_bytes(
            etree.tostring(target))


    def find_file_in_profiles_to_migrate(self, filename):
        return filter(methodcaller('isfile'),
                      map(methodcaller('joinpath', filename),
                          map(self.profile_path, self.profiles_to_migrate)))

    @property
    @instance.memoize
    def profiles_to_migrate(self):
        result = []
        for profile in self.read_dependencies('opengever.policy.base:default'):
            if not profile.startswith('opengever.'):
                continue
            elif profile in result:
                print '   WARNING: skipping duplicate profile', profile
            else:
                result.append(profile)
        return result

    def profile_path(self, profile):
        profile = re.sub('^profile-', '', profile)
        return (self.buildout_dir
                .joinpath(*profile.split(':')[0].split('.'))
                .joinpath('profiles', profile.split(':')[1])).abspath()

    def recursive_dependencies(self, profile):
        return map(self.read_dependencies, self.read_dependencies(profile))

    @instance.memoize
    def read_dependencies(self, profile):
        metadata_xml_path = (self.profile_path('opengever.policy.base:default')
                             .joinpath('metadata.xml'))
        if not metadata_xml_path.isfile() and metadata_xml_path.parent.isdir():
            return []

        with metadata_xml_path.open() as fio:
            doc = etree.parse(fio)

        result = []
        for node in doc.xpath('//dependency'):
            result.append(re.sub('^profile-', '', node.text.strip()))

        return result




if __name__ == '__main__':
    MergeTool()()
