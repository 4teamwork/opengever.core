from opengever.api.docsbuilder import SchemaDocsBuilder
import sys


buildout_dir = sys.argv[1]


print "Updating schema docs..."
builder = SchemaDocsBuilder(buildout_dir)
builder.build()
print "Schema docs updated.\n"
