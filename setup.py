from setuptools import setup, find_packages
import os

version = open('opengever/examplecontent/version.txt').read().strip()
maintainer = 'Florian Sprenger'

setup(name='opengever.examplecontent',
      version=version,
      maintainer = maintainer,
      description="Adds example content to an opengever site (Maintainer: %s)" % \
          maintainer,
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
      keywords='opengever example content',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='http://psc.4teamwork.ch/dist/opengever-examplecontent/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.transmogrifier',
          'collective.blueprint.jsonmigrator',
          'opengever.ogds.base',
          'collective.transmogrifier',
          'transmogrify.dexterity',
          'vs.genericsetup.ldap',
          'Products.PloneLDAP',
          'collective.blueprint.usersandgroups',
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone

      [opengever.setup]
      ldap = opengever.examplecontent
      policies = opengever.examplecontent
      """,
      )
