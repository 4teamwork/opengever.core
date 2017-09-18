from setuptools import find_packages
from setuptools import setup

import os


version = '2017.5.2.dev0'
maintainer = '4teamwork AG'


api_require = []

tests_require = [
    'ftw.builder',
    'ftw.flamegraph',
    'ftw.journal',
    'ftw.tabbedview',
    'ftw.table',
    'ftw.testbrowser',
    'ftw.testing',
    'lxml',
    'opengever.pdfconverter',
    'plone.app.dexterity',
    'plone.app.testing',
    'plone.formwidget.namedfile',
    'plone.mocktestcase',
    'plone.namedfile[blobs]',
    'plone.testing',
    'Products.CMFPlone',
    'PyJWT',
    'pyquery',
    'requests_toolbelt',
    'xlrd',
    'z3c.blobfile',
    'z3c.form',
    'z3c.saconfig',
    'zope.globalrequest',
    'zope.testing',
    'glob2',
]

setup(name='opengever.core',
      version=version,
      description="OpenGever Core (Maintainer: %s)" % maintainer,
      long_description=(
          open("README.rst").read() + "\n" +
          open(os.path.join("docs", "HISTORY.txt")).read()
          ),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
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
      namespace_packages=[
          'opengever',
          'opengever.ogds',
          'opengever.policy',
          'opengever.portlets',
      ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'alembic >= 0.7.0',
          'collective.autopermission',
          'collective.blueprint.jsonmigrator',
          'collective.blueprint.usersandgroups',
          'collective.dexteritytextindexer',
          'collective.elephantvocabulary',
          'collective.indexing',
          'collective.jqcookie',
          'collective.js.timeago',
          'collective.mtrsetup',
          'collective.quickupload >= 1.11.0',
          'collective.transmogrifier',
          'collective.usernamelogger',
          'collective.vdexvocabulary',
          'collective.z3cform.datagridfield',
          'docxcompose',
          'five.globalrequest',
          'five.grok',
          'ftw.builder',
          'ftw.bumblebee > 1.7.0',
          'ftw.casauth',
          'ftw.chameleon',
          'ftw.contentmenu >= 2.4.0',
          'ftw.contentstats',
          'ftw.copymovepatches',
          'ftw.datepicker',
          'ftw.dictstorage [sqlalchemy]',
          'ftw.inflator',
          'ftw.journal',
          'ftw.keywordwidget',
          'ftw.lawgiver',
          'ftw.mail',
          'ftw.pdfgenerator',
          'ftw.profilehook',
          'ftw.showroom',
          'ftw.structlog',
          'ftw.tabbedview[extjs, quickupload]',
          'ftw.table>=1.18.0',
          'ftw.tika',
          'ftw.upgrade >= 1.18.0',
          'ftw.usermigration',
          'ftw.zipexport',
          'jsonschema',
          'Markdown',
          'mr.bob',
          'ooxml_docprops',
          'opengever.ogds.models',
          'openpyxl',
          'ordereddict',
          'path.py',
          'Pillow',
          'plone.api >= 1.4.11',
          'plone.app.caching',
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
          'plone.rest',
          'plone.restapi',
          'plone.rfc822',
          'plone.supermodel',
          'plone.z3cform',
          'Plone',
          'plone4.csrffixes',
          'plonetheme.teamraum',
          'Products.LDAPUserFolder',
          'Products.PloneLDAP',
          'python-ldap',
          'pytz',
          'PyXB',
          'requests',
          'setuptools',
          'sqlalchemy-i18n',
          'SQLAlchemy',
          'subprocess32',
          'transmogrify.dexterity',
          'tzlocal',
          'ua-parser',
          'vs.genericsetup.ldap',
          'xlrd',
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
          api=api_require,
          tests=tests_require,
      ),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      [zopectl.command]
      sync_ogds = opengever.ogds.base:sync_ogds_zopectl_handler
      dump_schemas = opengever.base.schemadump:dump_schemas_zopectl_handler
      import = opengever.bundle.console:import_oggbundle

      [izug.basetheme]
      version = opengever.core

      [console_scripts]
      create-policy = opengever.policytemplates.cli:main
      pyxbgen = opengever.disposition.ech0160.pyxbgen:main
      """,
      )
