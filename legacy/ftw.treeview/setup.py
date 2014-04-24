from setuptools import setup, find_packages
import os

version = '1.0.4.dev0'

setup(name='ftw.treeview',
      version=version,
      description='Adds a navigation treeview widget to plone.',

      long_description=open("README.rst").read() + "\n" + \
                       open(os.path.join("docs", "HISTORY.txt")).read(),

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.0',
        'Framework :: Plone :: 4.1',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.treeview',

      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
          'setuptools',
          'collective.jqcookie',
          # 'ftw.dictstorage',
      ],

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
