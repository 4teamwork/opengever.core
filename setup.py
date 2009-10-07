from setuptools import setup, find_packages
import os

version = open('opengever/journal/version.txt').read().strip()

setup(name='opengever.journal',
      version=version,
      description="Opengever Journal integrates ftw.journal",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='opengever journal ftw.journal',
      author='Jonas Baumann, 4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='http://psc.4teamwork.ch/4teamwork/kunden/opengever/opengever.journal',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'ftw.journal',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
