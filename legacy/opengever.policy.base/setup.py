from setuptools import setup, find_packages
import os

version = open('opengever/policy/base/version.txt').read().strip()
maintainer = 'Thomas Buchberger'

setup(name='opengever.policy.base',
      version=version,
      description="Basic policy for installing OpenGever without any client specific dependencies %s" % (maintainer),
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://www.4teamwork.ch',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever', 'opengever.policy'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ftw.datepicker',
          'opengever.base',
          'opengever.document',
          'opengever.dossier',
          'opengever.globalindex',
          'opengever.inbox',
          'opengever.journal',
          'opengever.ogds.base',
          'opengever.portlets.tree',
          'opengever.repository',
          'opengever.tabbedview',
          'opengever.tasktemplates',
          'opengever.task',
          'opengever.trash',
          'opengever.contact',
          'opengever.latex',
          'opengever.advancedsearch',
          'opengever.sharing',
          'izug.basetheme',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
