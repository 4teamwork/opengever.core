from setuptools import setup, find_packages
import os

version = open('opengever/document/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require = [
    'collective.testcaselayer',
    'plone.app.testing',
    'opengever.ogds.base[tests]'
]

setup(name='opengever.document',
      version=version,
      description="OpenGever Document content type (Maintainer: %s)" % maintainer,
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
      keywords='opengever document',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/opengever-document/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zc.relation',
        'z3c.form',
        'z3c.relationfield',
        'plone.z3cform',
        'plone.supermodel',
        'plone.rfc822',
        'plone.registry',
        'plone.namedfile[blobs]',
        'plone.directives.form',
        'plone.directives.dexterity',
        'plone.dexterity',
        'plone.autoform',
        'opengever.base',
        'setuptools',
        #'Products.ARFilePreview',
        #'collective.filepreviewbehavior',
        'plone.app.dexterity',
        'plone.app.registry',
        'plone.principalsource',
        'plone.app.versioningbehavior',
        'ftw.journal',
        'opengever.task',
        'opengever.tabbedview',
        'opengever.trash',
        'opengever.ogds.base',
        'collective.autopermission',
        'collective.vdexvocabulary',
        'collective.elephantvocabulary',
        'plone.formwidget.contenttree',
        'plone.app.lockingbehavior',
        'ftw.datepicker',
        'opengever.dossier',
        'collective.dexteritytextindexer',
        'opengever.mail',
        ],

        tests_require=tests_require,
        extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
