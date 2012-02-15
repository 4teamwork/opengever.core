from setuptools import setup, find_packages
import os


version = open('opengever/contact/version.txt').read().strip()
maintainer = 'Philippe Gross'

tests_require = [
    'plone.formwidget.namedfile',
    'plone.app.testing',
    'opengever.repository',
    ]

setup(name='opengever.contact',
      version=version,
      description="the contactfolder and contact types" + \
          ' (Maintainer: %s)' % maintainer,
      long_description=open("README.txt").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='opengever contact',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/4teamwork/dist/opengever-contact/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'plone.namedfile[blobs]',
        'plone.dexterity',
        'ftw.table',
        'setuptools',
        'five.grok',
        'opengever.tabbedview',
        'collective.dexteritytextindexer',
        'plone.app.lockingbehavior',
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
