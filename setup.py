from setuptools import setup, find_packages
import os

version = open('opengever/document/version.txt').read().strip()
maintainer = 'Jonas Baumann'

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
      url='http://psc.4teamwork.ch/4teamwork/kunden/opengever/opengever.document/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.ARFilePreview',
        'Products.CMFCore',
        'Products.MimetypesRegistry',
        'collective.filepreviewbehavior',
        'ftw.sendmail',
        'opengever.sqlfile',
        'plone.app.dexterity',
        'plone.app.registry',
        'plone.principalsource',
        'plone.stagingbehavior',
        'plone.versioningbehavior',
        'stoneagehtml', # required by ftw.sendmail, but there is no dependency in the current release
        'ftw.datepicker',
        'ftw.directoryservice',
        'ftw.table',
        'ftw.journal',
        'ftw.task',
        'opengever.dossier',
        'opengever.tabbedview',
        'opengever.repository',
        'opengever.inbox',
        'opengever.octopus.tentacle',
        'opengever.translations',
        'collective.autopermission',
        'collective.testcaselayer',
        'plone.keyring',
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
