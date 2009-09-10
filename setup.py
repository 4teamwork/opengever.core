from setuptools import setup, find_packages
import os

version = '0.1-dev'

setup(name='opengever.document',
      version=version,
      description="OpenGever Document content type",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='opengever document',
      author='Jonas Baumann, \xc34teamwork GmbH',
      author_email='info\xc6@4teamwork.ch',
      url='https://svn.4teamwork.ch/repos/opengever/opengever.document/',
      license='GPL2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['opengever'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
