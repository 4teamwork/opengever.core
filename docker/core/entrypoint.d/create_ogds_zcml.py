# Create OGDS ZCML include from environment variables

from os import environ


def main():
    ogds_zcml_file = '/app/etc/package-includes/001-ogds-overrides.zcml'

    url = environ.get(
        'OGDS_URL', 'postgresql+psycopg2://ogds:secret@ogds:5432/ogds')
    pool_recycle = environ.get('OGDS_POOL_RECYCLE', '3600')

    ogds_zcml = OGDS_ZCML_TEMPLATE.format(url=url, pool_recycle=pool_recycle)

    with open(ogds_zcml_file, 'w') as file_:
        file_.write(ogds_zcml)


OGDS_ZCML_TEMPLATE = """\
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:db="http://namespaces.zope.org/db">

    <include package="z3c.saconfig" file="meta.zcml" />

    <db:engine name="opengever.db"
      url="{url}" pool_recycle="{pool_recycle}" />
    <db:session name="opengever" engine="opengever.db" />
</configure>
"""


if __name__ == "__main__":
    main()
