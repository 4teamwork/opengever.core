from setuptools import setup, find_packages
import os

version = open('opengever/task/version.txt').read().strip()
maintainer = 'Philippe Gross'

tests_require = [
    'lxml >= 2.1.1',
    'z3c.form [test]',
    'z3c.saconfig',
    'plone.app.testing',
    'opengever.document',
    'opengever.contact',
    'ftw.tabbedview',
    'ftw.contentmenu',
    'ftw.testing',
    ]

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
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-task',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'plone.app.dexterity',
        'plone.app.registry',
        'rwproperty',
        'collective.autopermission',
        'opengever.base',
        'opengever.ogds.base',
        'opengever.globalindex',
        'opengever.tabbedview',
        'ftw.table',
        'ftw.datepicker',
        'five.globalrequest',
        'collective.vdexvocabulary',
        'ftw.contentmenu',
        'collective.elephantvocabulary',
        'plone.app.lockingbehavior',
        'collective.dexteritytextindexer',
        'opengever.trash',
       ],
      tests_require=tests_require,
      extras_require = dict(tests=tests_require),
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
