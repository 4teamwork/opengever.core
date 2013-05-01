from setuptools import setup, find_packages
import os

version = open('opengever/journal/version.txt').read().strip()
maintainer = 'Jonas Baumann'
tests_require = ['ftw.table',
                 'ftw.tabbedview',
                 'ftw.journal',
                 'opengever.ogds.base',
                 'opengever.document',
                 'opengever.dossier',
                 'opengever.task',
                 'opengever.trash',
                 'opengever.mail',
                 'opengever.contact',
                 'opengever.repository',
                 'plone.app.testing',]
setup(name='opengever.journal',
      version=version,
      description="Opengever Journal integrates ftw.journal (Maintainer: %s)" % \
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
      keywords='opengever journal ftw.journal',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever.journal',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'plone.dexterity',
        'ftw.table',
        'ftw.tabbedview',
        'ftw.mail',
        'opengever.trash',
        'opengever.task',
        'opengever.dossier',
        'opengever.document',
        'opengever.tabbedview',
        'setuptools',
        'ftw.journal',
        'plone.app.versioningbehavior',
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
