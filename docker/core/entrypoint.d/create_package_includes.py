# Create package includes from environment variables

from os import environ


def main():
    zcml_include_file = '/app/etc/package-includes/999-additional-overrides.zcml'
    packages = environ.get('ZCML_PACKAGE_INCLUDES', '')

    if not packages:
        return

    package_includes = '\n'.join(
        [PACKAGE_INCLUDE.format(package_name=p) for p in packages.split(' ')])
    zcml = ZCML_TEMPLATE.format(package_includes=package_includes)

    with open(zcml_include_file, 'w') as file_:
        file_.write(zcml)


PACKAGE_INCLUDE = """  <include package="{package_name}" />"""
ZCML_TEMPLATE = """\
<configure xmlns="http://namespaces.zope.org/zope">
{package_includes}
</configure>
"""


if __name__ == "__main__":
    main()
