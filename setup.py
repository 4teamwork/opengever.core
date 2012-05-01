from setuptools import setup, find_packages
import os

version = open('opengever/tabbedview/version.txt').read().strip()
maintainer = 'Victor Baumann'

tests_require = [
    'plone.app.testing',
    'opengever.repository',
    ]


setup(name='opengever.tabbedview',
      version=version,
      description="opengever integration for ftw.tabbedview (Maintainer %s)" % \
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
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-tabbedview/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'five.grok',
        'ftw.journal',
        'ftw.mail',
        'ftw.tabbedview[extjs, quickupload]',
        'opengever.base',
        'opengever.globalindex',
        'opengever.ogds.base',
        'opengever.task',
        'plone.app.dexterity',
        'z3c.autoinclude',
          #'collective.jqhistory'
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
