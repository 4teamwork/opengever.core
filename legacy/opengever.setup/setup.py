from setuptools import setup, find_packages
import os

version = open('opengever/setup/version.txt').read().strip()
maintainer = 'Jonas Baumann'

setup(name='opengever.setup',
      version=version,
      description="opengever setup wizard" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='opengever setup wizard',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever.setup/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'collective.blueprint.jsonmigrator',
        'collective.transmogrifier',
        'opengever.globalindex',
        'opengever.ogds.base',
        'opengever.mail',
        'opengever.portlets.tree',
        'plone.app.transmogrifier',
        'plone.dexterity',
        'plone.registry',
        'setuptools',
        'transmogrify.dexterity',
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
