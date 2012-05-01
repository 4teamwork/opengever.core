from setuptools import setup, find_packages
import os

version = open('opengever/mail/version.txt').read().strip()
maintainer = 'Julian Infanger'

tests_require = [
    'plone.app.testing',
    'opengever.dossier',
    'opengever.ogds.base[tests]',
    'opengever.base',
    'Products.CMFPlone',
    'opengever.document',
    'ftw.testing',
    ]

extras_require = {
    # Adding opengever.document to install_requires will result in circular
    # dependencies. This extras prevents ftw.manager from sugesting this
    # dependency.
    'document': ['opengever.document'],
    'tests': tests_require,
}

setup(name='opengever.mail',
      version=version,
      description="OpenGever Mail (Maintainer: %s)" % maintainer,
      long_description=open("README.txt").read() + "\n" + \
        open(os.path.join("docs", "HISTORY.txt")).read(),
        # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever.mail/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'plone.z3cform',
        'plone.formwidget.autocomplete',
        'opengever.base',
        'z3c.relationfield',
        'z3c.form',
        'plone.namedfile[blobs]',
        'plone.dexterity',
        'opengever.tabbedview',
        'plone.registry',
        'ftw.mail',
        'opengever.ogds.base',
        'ftw.table',
        'setuptools',
        'plone.app.dexterity',
        'plone.app.registry',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=extras_require,
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
