from setuptools import setup, find_packages
import os

version = '4.7.4.dev0'
maintainer = '4teamwork AG'


api_require = [
    'plone.restapi',
]

tests_require = [
    'Products.CMFPlone',
    'ftw.journal',
    'ftw.tabbedview',
    'ftw.table',
    'ftw.testbrowser',
    'ftw.testing',
    'lxml',
    'plone.app.dexterity',
    'plone.app.testing',
    'plone.formwidget.namedfile',
    'plone.mocktestcase',
    'plone.namedfile[blobs]',
    'plone.testing',
    'pyquery',
    'xlrd',
    'z3c.blobfile',
    'z3c.form',
    'z3c.saconfig',
    'zope.globalrequest',
    'zope.testing',
    'ftw.builder',
]

setup(name='opengever.core',
      version=version,
      description="OpenGever Core (Maintainer: %s)" % maintainer,
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author=maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://github.com/4teamwork/opengever.core',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever', 'opengever.policy', 'opengever.ogds', 'opengever.portlets'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        # Remove ftw.treeview when uninstall upgrade installed.
        'ftw.treeview',

        'alembic >= 0.7.0',
        'collective.autopermission',
        'collective.blueprint.jsonmigrator',
        'collective.blueprint.usersandgroups',
        'collective.dexteritytextindexer',
        'collective.elephantvocabulary',
        'collective.jqcookie',
        'collective.js.timeago',
        'collective.mtrsetup',
        'collective.quickupload',
        'collective.transmogrifier',
        'collective.usernamelogger',
        'collective.vdexvocabulary',
        'collective.z3cform.datagridfield',
        'five.globalrequest',
        'five.grok',
        'ftw.builder',
        'ftw.casauth',
        'ftw.contentmenu >= 2.4.0',
        'ftw.datepicker',
        'ftw.dictstorage [sqlalchemy]',
        'ftw.footer',
        'ftw.inflator',
        'ftw.journal',
        'ftw.mail',
        'ftw.pdfgenerator',
        'ftw.profilehook',
        'ftw.tabbedview[extjs, quickupload]',
        'ftw.table',
        'ftw.tooltip',
        'ftw.upgrade >= 1.18.0',
        'ftw.zipexport',
        'Markdown',
        'mr.bob',
        'ooxml_docprops',
        'opengever.ogds.models',
        'ordereddict',
        'Pillow',
        'Plone',
        'plone.api',
        'plone.app.dexterity [grok, relations]',
        'plone.app.lockingbehavior',
        'plone.app.registry',
        'plone.app.relationfield',
        'plone.app.transmogrifier',
        'plone.app.versioningbehavior',
        'plone.autoform',
        'plone.dexterity',
        'plone.directives.dexterity',
        'plone.directives.form',
        'plone.formwidget.autocomplete',
        'plone.formwidget.contenttree',
        'plone.formwidget.namedfile',
        'plone.namedfile[blobs]',
        'plone.principalsource',
        'plone.protect >= 3.0.15',
        'plone.registry',
        'plone.rfc822',
        'plone.supermodel',
        'plone.z3cform',
        'plone4.csrffixes',
        'Products.LDAPUserFolder',
        'Products.PloneLDAP',
        'python-ldap',
        'pytz',
        'requests',
        'rwproperty',
        'setuptools',
        'SQLAlchemy',
        'sqlalchemy-i18n',
        'subprocess32',
        'transmogrify.dexterity',
        'tzlocal',
        'vs.genericsetup.ldap',
        'xlrd',
        'xlwt',
        'z3c.autoinclude',
        'z3c.form',
        'z3c.formwidget.query',
        'z3c.relationfield',
        'z3c.saconfig',
        'zc.relation',
        'zope.globalrequest',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(
          tests=tests_require,
          api=api_require,
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      [zopectl.command]
      sync_ogds = opengever.ogds.base:sync_ogds_zopectl_handler
      dump_schemas = opengever.base.schemadump:dump_schemas_zopectl_handler

      [izug.basetheme]
      version = opengever.core

      [console_scripts]
      create-policy = opengever.policytemplates.cli:main
      """,
      )
