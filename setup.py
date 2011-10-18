from setuptools import setup, find_packages
import os

version = open('opengever/tasktemplates/version.txt').read().strip()
maintainer = 'Victor Baumann'

tests_require = [
    'plone.app.testing',
    'opengever.task',
    'opengever.dossier',
    'opengever.tabbedview',
    'opengever.contact',
    'opengever.document',
    'ftw.table',
    'ftw.contentmenu',
    'plone.mocktestcase',
    ]

setup(name='opengever.tasktemplates',
      version=version,
      description="" + \
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
      keywords='opengever task templates',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-tasktemplates/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zope.globalrequest',
        'z3c.form',
        'plone.formwidget.autocomplete',
        'plone.dexterity',
        'opengever.task',
        'opengever.tabbedview',
        'opengever.ogds.base',
        'opengever.dossier',
        'five.grok',
        'plone.directives.form',
        'ftw.table',
        'setuptools',
        'plone.app.lockingbehavior',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require = dict(tests=tests_require),
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
