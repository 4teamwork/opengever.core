from setuptools import setup, find_packages
import os

version = open('opengever/advancedsearch/version.txt').read().strip()
maintainer = 'Philippe Gross'

tests_require = [
    'plone.app.testing',
    'opengever.ogds.base [tests]',
    'opengever.base',
    'opengever.document',
    'opengever.dossier',
    'opengever.contact',
    'opengever.task'
    ]

setup(name='opengever.advancedsearch',
      version=version,
      description="Advanced search for opengever (Maintainer: %s)" % maintainer,
      long_description=open("README.txt").read() + "\n" +
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
      url='http://psc.4teamwork.ch/dist/opengever.advancedsearch/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'z3c.form',
          'setuptools',
          'opengever.ogds.base',
          'opengever.task',
          'ftw.datepicker',
          'plone.dexterity',
          'plone.app.registry',
          'opengever.globalindex',
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
