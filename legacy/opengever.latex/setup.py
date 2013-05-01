from setuptools import setup, find_packages
import os

version = open('opengever/latex/version.txt').read().strip()
maintainer = 'Jonas Baumann'

tests_require = [
    'ftw.testing',
    'plone.testing',
    ]

setup(name='opengever.latex',
      version=version,
      description="Opengever latex views" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='opengever latex views',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-latex',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'plone.registry',
        'plone.autoform',
        'opengever.tabbedview',
        'opengever.globalindex',
        'opengever.repository',
        'opengever.task',
        'opengever.repository',
        'opengever.ogds.base',
        'opengever.dossier',
        'opengever.base',
        'ftw.table',
        'ftw.pdfgenerator',
        'setuptools',
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
