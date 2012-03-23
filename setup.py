from setuptools import setup, find_packages
import os

version = open('opengever/dossier/version.txt').read().strip()
maintainer = 'Thomas Buchberger'

tests_require = [
    'plone.app.testing',
    'opengever.task',
    'opengever.document',
    'opengever.globalindex',
    'plone.mocktestcase',
]

setup(name='opengever.dossier',
      version=version,
      description="OpenGever Dossier Content Types (Maintainer: %s)" % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='OpenGever Dossier',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever.dossier/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'ftw.contentmenu',
        'plone.registry',
        'opengever.repository',
        'collective.elephantvocabulary',
        'z3c.relationfield',
        'z3c.form',
        'plone.z3cform',
        'plone.namedfile',
        'plone.formwidget.contenttree',
        'plone.formwidget.autocomplete',
        'plone.dexterity',
        'plone.autoform',
        'opengever.tabbedview',
        'ftw.tabbedview',
        'opengever.ogds.base',
        'ftw.table',
        'ftw.datepicker',
        'setuptools',
        'plone.app.dexterity',
        'plone.app.registry',
        'collective.autopermission',
        'opengever.base',
        'rwproperty',
        'opengever.mail',
        'opengever.sharing',
        'collective.vdexvocabulary',
        'collective.dexteritytextindexer',
        'plone.app.lockingbehavior',
        'izug.basetheme',
        'collective.z3cform.datagridfield',
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
