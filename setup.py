from setuptools import setup, find_packages
import os

version = open('opengever/mail/version.txt').read().strip()
maintainer = 'Julian Infanger'

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
      url='http://psc.4teamwork.ch/4teamwork/kunden/opengever/opengever.mail/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'plone.registry',
        'ftw.mail',
        'setuptools',
        'Plone',
        'plone.app.dexterity',
        'plone.app.registry',
        'collective.testcaselayer',
        # -*- Extra requirements: -*-
        ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = opengever
      """,
      )
