from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ftw.task',
      version=version,
      description="the ftw task object",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='phgross',
      author_email='philippe.gross@4teamwork.ch',
      url='www.4teamwork.ch',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.dexterity',
          'plone.app.contentrules',
          'plone.app.registry',
          'rwproperty',
          'ftw.datepicker',
          'collective.autopermission',
          'opengever.base',
          'collective.testcaselayer',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
