from setuptools import setup, find_packages
import os

version = open('opengever/repository/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require = [
    'collective.testcaselayer',
    'Products.PloneTestCase',
    'opengever.ogds.base[tests]',
    'ftw.testing',
    ]

setup(name='opengever.repository',
      version=version,
      description="OpenGever Repository (Maintainer: %s)" % maintainer,
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
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='https://svn.4teamwork.ch/dist/opengever-repository/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'z3c.form',
        'plone.registry',
        'plone.dexterity',
        'setuptools',
        'plone.app.dexterity',
        'plone.app.registry',
        'opengever.base',
        'opengever.tabbedview',
        'collective.autopermission',
        'plone.app.lockingbehavior',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
