from setuptools import setup, find_packages
import os

version = open('opengever/task/version.txt').read().strip()
maintainer = 'Philippe Gross'

setup(name='opengever.task',
      version=version,
      description="the opengever task object" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      url='http://psc.4teamwork.ch/4teamwork/opengever/opengever.task',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
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
          'opengever.translations',
          'collective.testcaselayer',
          # -*- Extra requirements: -*-
      ],
      extras_require = dict(
        test = [
            'lxml >= 2.1.1',
        ],
      ),
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
