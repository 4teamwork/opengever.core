# Usage: bin/zopepy ./docker/scripts/autoinclude2zcml.py >./docker/etc/site.zcml
from z3c.autoinclude.plugin import PluginFinder

ZCML_FILENAMES = ['meta.zcml', 'configure.zcml', 'overrides.zcml']

SITE_ZCML_HEAD = """<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:meta="http://namespaces.zope.org/meta"
    xmlns:five="http://namespaces.zope.org/five">

  <meta:provides feature="disable-autoinclude" />

  <include package="Zope2.App" />
  <include package="Products.Five" />
  <meta:redefinePermission from="zope2.Public" to="zope.Public" />

  <!-- Load the meta -->
  <include files="package-includes/*-meta.zcml" />
  <five:loadProducts file="meta.zcml"/>

  <!-- Load the configuration -->
  <include files="package-includes/*-configure.zcml" />
  <five:loadProducts />

  <!-- Load the configuration overrides-->
  <includeOverrides files="package-includes/*-overrides.zcml" />
  <five:loadProductsOverrides />

  <securityPolicy
      component="AccessControl.security.SecurityPolicy" />
"""

SITE_ZCML_TAIL = """
</configure>
"""


def main():
    plugin_finder = PluginFinder('plone')
    info = plugin_finder.includableInfo(
        ZCML_FILENAMES)

    print(SITE_ZCML_HEAD)

    for zcml_filename in ZCML_FILENAMES:
        for package in info[zcml_filename]:
            if zcml_filename == 'overrides.zcml':
                print('  <includeOverrides package="{}" file="{}" />'.format(
                    package, zcml_filename))
            else:
                print('  <include package="{}" file="{}" />'.format(
                    package, zcml_filename))

    print(SITE_ZCML_TAIL)


if __name__ == '__main__':
    main()
