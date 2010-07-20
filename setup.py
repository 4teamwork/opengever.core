from setuptools import setup, find_packages
import os

version = open('opengever/base/version.txt').read().strip()
maintainer = 'Jonas Baumann'

setup(name='opengever.base',
      version=version,
      description="Base package for OpenGever (Maintainer: %s)" % maintainer,
      long_description=open("README.txt").read() + "\n" + \
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
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/4teamwork/kunden/opengever/opengever.base/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zope.schema',
        'zope.publisher',
        'zope.lifecycleevent',
        'zope.interface',
        'zope.i18nmessageid',
        'zope.component',
        'zope.app.container',
        'zope.annotation',
        'z3c.form',
        'plone.z3cform',
        'plone.indexer',
        'plone.formwidget.namedfile',
        'plone.app.dexterity',
        'opengever.repository',
        'opengever.dossier',
        'opengever.document',
        'ftw.table',
        'Products.PloneTestCase',
        'Products.CMFCore',
        'setuptools',
        'plone.dexterity',
        'opengever.tabbedview',
        'plone.autoform',
        'collective.testcaselayer',
        'collective.monkeypatcher',
        'plone.registry',
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = opengever
      """,
      )
