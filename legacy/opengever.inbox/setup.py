from setuptools import setup, find_packages
import os

version = open('opengever/inbox/version.txt').read().strip()
maintainer = 'Thomas Buchberger'

tests_require = [
    'plone.app.testing',
    'opengever.ogds.base[tests]',
    'opengever.document',
    'opengever.task',
    'ftw.testing',
    ]

setup(name='opengever.inbox',
      version=version,
      description="Inbox for OpenGever (Maintainer: %s)"  % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='opengever inbox',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-inbox/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'z3c.relationfield',
        'z3c.form',
        'plone.registry',
        'plone.formwidget.contenttree',
        'plone.directives.dexterity',
        'ftw.contentmenu',
        'plone.dexterity',
        'opengever.ogds.base',
        'opengever.mail',
        'setuptools',
        'opengever.dossier',
        'opengever.tabbedview',
        'opengever.globalindex',
        'opengever.trash',
        'opengever.base',
        'opengever.task',

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
