from setuptools import setup, find_packages
import os

version = open('opengever/ogds/base/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require = [
    'plone.app.testing',
    'plone.app.dexterity',
    'opengever.globalindex',
    'opengever.contact',
    'opengever.repository',
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
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever/opengever-ogds-base',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever', 'opengever.ogds'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'SQLAlchemy',
        'collective.elephantvocabulary',
        'collective.transmogrifier',
        'five.globalrequest',
        'five.grok',
        'ftw.dictstorage [sqlalchemy]',
        'ftw.dictstorage',
        'plone.app.registry',
        'plone.dexterity',
        'plone.formwidget.autocomplete',
        'transmogrify.sqlinserter',
        'plone.namedfile[blobs]',
        'python-ldap',
        'setuptools',
        'z3c.form',
        'z3c.formwidget.query',
        'z3c.relationfield',
        'z3c.saconfig',
        'zope.globalrequest',
        'opengever.ogds.models',
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
