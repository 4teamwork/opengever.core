from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='opengever.inbox',
      version=version,
      description="Inbox for OpenGever",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Thomas Buchberger',
      author_email='t.buchberger@4teamwork.ch',
      url='http://www.4teamwork.ch',
      license='GPL',
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

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
