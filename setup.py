from setuptools import setup, find_packages
import os

version = open('opengever/ogds/base/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.app.testing',
    'opengever.contact',
    'plone.app.dexterity',
    ]

setup(name='opengever.ogds.base',
      version=version,
      description="OpenGever directory service base package" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='opengever ogds base',
      author='%s, 4teamwork GmbH',
      author_email='GPL2',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/4teamwork/kunden/' + \
          'opengever/opengever-ogds-base',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever', 'opengever.ogds'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zope.globalrequest',
        'z3c.relationfield',
        'z3c.formwidget.query',
        'z3c.form',
        'plone.testing',
        'plone.registry',
        'plone.namedfile',
        'plone.formwidget.autocomplete',
        'plone.dexterity',
        'opengever.tabbedview',
        'opengever.globalindex',
        'ftw.table',
        'ftw.tabbedview',
        'ftw.dictstorage',
        'setuptools',
        'SQLAlchemy',
        'five.globalrequest',
        'five.grok',
        'python-ldap',
        'plone.app.registry',
        'z3c.saconfig',
        'collective.elephantvocabulary',
        'collective.transmogrifier',
        'opengever.konsulmigration',
        'ftw.dictstorage [sqlalchemy]',
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
