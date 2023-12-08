# Create Solr ZCML include from environment variables

from os import environ


def main():
    solr_zcml_file = '/app/etc/package-includes/002-solr-overrides.zcml'

    host = environ.get('SOLR_HOST', 'solr')
    port = environ.get('SOLR_PORT', '8983')
    base = environ.get('SOLR_BASE', '/solr/ogsite')
    upload_blobs = environ.get('SOLR_UPLOAD_BLOBS', 'true')

    solr_zcml = SOLR_ZCML_TEMPLATE.format(
        host=host, port=port, base=base, upload_blobs=upload_blobs)

    with open(solr_zcml_file, 'w') as file_:
        file_.write(solr_zcml)


SOLR_ZCML_TEMPLATE = """\
<configure xmlns:solr="http://namespaces.plone.org/solr">
    <include package="ftw.solr" file="meta.zcml" />
    <solr:connection host="{host}"
                     port="{port}"
                     base="{base}"
                     upload_blobs="{upload_blobs}"/>
</configure>

"""


if __name__ == "__main__":
    main()
