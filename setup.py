from setuptools import setup, find_packages
import os

version = open('opengever/repository/version.txt').read().strip()

setup(name='opengever.repository',
      version=version,
      description="OpenGever Repository",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Jonas Baumann',
      author_email='mailto:info@4teamwork.ch',
      url='https://svn.4teamwork.ch/repos/opengever/opengever.repository/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'collective.autopermission',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      # -*- Entry points: -*-
      """,
      )
