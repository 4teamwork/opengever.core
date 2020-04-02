from setuptools import find_packages
from setuptools import setup

import os


version = '2019.6.4'
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
    'glob2',
    'lxml',
    'mock',
    'plone.app.dexterity',
    'plone.app.testing',
    'plone.formwidget.namedfile',
    'plone.mocktestcase',
    'plone.namedfile[blobs]',
    'plone.resource',
    'plone.testing',
    'Products.CMFPlone',
    'PyJWT',
    'pyquery',
    'requests_mock',
    'requests_toolbelt',
    'xlrd',
    'z3c.blobfile',
    'z3c.form',
    'z3c.saconfig',
    'zope.globalrequest',
    'zope.testing',
]

solr_conf_files = [
    os.path.join(parent, name)
    for (parent, subdirs, files) in os.walk('solr-conf')
    for name in files + subdirs
]

setup(name='opengever.core',
      version=version,
      description="OpenGever Core (Maintainer: %s)" % maintainer,
      long_description=(
          open("README.rst").read() + "\n"
          + open(os.path.join("docs", "HISTORY.txt")).read()
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
          'plonetheme',
      ],
      include_package_data=True,
      data_files=[
          ('solr-conf', solr_conf_files),
      ],
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
          'docxcompose >= 1.0.0a17',
          'five.globalrequest',
          'ftw.builder',
          'ftw.bumblebee > 1.7.0',
          'ftw.casauth',
          'ftw.catalogdoctor',
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
          'ftw.mobilenavigation',
          'ftw.pdfgenerator',
          'ftw.profilehook',
          'ftw.showroom',
          'ftw.solr',
          'ftw.structlog',
          'ftw.tabbedview[extjs, quickupload]',
          'ftw.table>=1.18.0',
          'ftw.tika',
          'ftw.tokenauth',
          'ftw.upgrade >= 1.18.0',
          'ftw.usermigration',
          'ftw.zipexport',
          'jsonschema',
          'Markdown',
          'mr.bob',
          'openpyxl',
          'ordereddict',
          'path.py',
          'Pillow',
          'Plone',
          'plone.api >= 1.4.11',
          'plone.app.caching',
          'plone.app.dexterity [relations]',
          'plone.app.lockingbehavior',
          'plone.app.registry',
          'plone.app.relationfield',
          'plone.app.theming',
          'plone.app.transmogrifier',
          'plone.app.versioningbehavior',
          'plone.autoform',
          'plone.dexterity',
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
          'plone4.csrffixes',
          'Products.CMFCore',
          'Products.LDAPUserFolder',
          'Products.PloneLDAP',
          'Products.statusmessages',
          'psutil',
          'python-ldap',
          'pytz',
          'PyXB',
          'requests',
          'setuptools',
          'SQLAlchemy',
          'sqlalchemy-i18n',
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
          'z3c.unconfigure',
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
      send_digest = opengever.activity:send_digest_zopectl_handler
      generate_overdue_notifications = opengever.dossier.cronjobs:generate_overdue_notifications_zopectl_handler
      generate_remind_notifications = opengever.task.reminder.cronjobs:generate_remind_notifications_zopectl_handler
      run_nightly_jobs = opengever.nightlyjobs.cronjobs:run_nightly_jobs_handler

      [console_scripts]
      create-policy = opengever.policytemplates.cli:main
      pyxbgen = opengever.disposition.ech0160.pyxbgen:main
      create-bundle = opengever.bundle.factory:main
      """,
      )
