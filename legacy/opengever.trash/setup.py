from setuptools import setup, find_packages
import os

version = open('opengever/trash/version.txt').read().strip()
maintainer = 'Philippe Gross'

tests_require = [
    'plone.app.testing',
    'plone.app.dexterity',
    'zope.globalrequest', # XXX Missing TinyMCE dependency. Remove as soon as it's fixed in TinyMCE
    'plone.namedfile[blobs]', # XXX Missing TinyMCE dependency. Remove as soon as it's fixed in TinyMCE
]
setup(name='opengever.trash',
      version=version,
      description="the opengever trash packet, implements the special delete " + \
          "funcitionalty. (Maintainer: %s)" % maintainer,
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
      keywords='opengever trash',
      author='%s, 4teamwork GmbH' % maintainer,
      author_email='mailto:info@4teamwork.ch',
      maintainer=maintainer,
      url='http://psc.4teamwork.ch/dist/opengever-trash/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'collective.autopermission',
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
