from setuptools import setup, find_packages
import os

version = open('opengever/journal/version.txt').read().strip()
maintainer = 'Jonas Baumann'

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
      url='http://psc.4teamwork.ch/4teamwork/kunden/opengever/opengever.journal',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'opengever.trash',
        'opengever.task',
        'opengever.dossier',
        'opengever.document',
        'setuptools',
        'ftw.journal',
        'plone.versioningbehavior',
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = opengever
      """,
      )
