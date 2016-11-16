#!/usr/bin/env python

from __future__ import print_function
import pyxb.xmlschema
import pyxb.binding.generate
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import optparse
import traceback

import logging
logging.basicConfig()
log_ = logging.getLogger(__name__)


def WSDLToSchema(generator, wsdl_uri):
    """Extract the schema element from a WSDL types document and
    generate bindings for it.

    This is expected to be equivalent to retrieving the WSDL,
    extracting the schema part of its C{types} block to a file, and
    using that file as a C{--schema-location}.  Note that use of this
    option may require availability of the WS-* bundle."""
    import pyxb.bundles.wssplat.wsdl11 as wsdl
    wsdl.ImportRelatedNamespaces()
    wsdl_uri = pyxb.utils.utility.NormalizeLocation(wsdl_uri)
    print('Retrieving WSDL from %s' % (wsdl_uri,))
    xmld = pyxb.utils.utility.DataFromURI(wsdl_uri)
    spec = wsdl.definitions.createFromDOM(pyxb.utils.domutils.StringToDOM(xmld, location_base=wsdl_uri), process_schema=True, generation_uid=generator.generationUID())
    return spec.schema()


def _WSDLOptionCallback(option, opt_str, value, parser, *args, **kwargs):
    assert parser.has_option('--schema-location')
    if parser.values.schema_location is None:
        parser.values.schema_location = []
    parser.values.schema_location.append((value, WSDLToSchema))


def main():
    generator = pyxb.binding.generate.Generator()
    parser = generator.optionParser()
    group = optparse.OptionGroup(parser, 'WSDL Options', 'Options relevant to generating bindings from WSDL service descriptions')
    group.add_option('-W', '--wsdl-location', metavar='FILE_or_URL',
                      action='callback', callback=_WSDLOptionCallback, type="string",
                      help=\
    '''Generate bindings for the C{types} element of the WSDL at this
    location.''')
    parser.add_option_group(group)

    (options, args) = parser.parse_args()

    generator.applyOptionValues(options, args)

    generator.resolveExternalSchema()

    if 0 == len(generator.namespaces()):
        parser.print_help()
        sys.exit(1)

    # Save binding source first, so name-in-binding is stored in the
    # parsed schema file
    try:
        tns = generator.namespaces().pop()
        modules = generator.bindingModules()
        print('Python for %s requires %d modules' % (tns, len(modules)))

        top_module = None
        path_dirs = set()
        for m in modules:
            m.writeToModuleFile()

        generator.writeNamespaceArchive()
    except Exception as e:
        print('Exception generating bindings: %s' % (e,))
        traceback.print_exception(*sys.exc_info())
        sys.exit(3)

if __name__ == '__main__':
    main()

# LocalVariables:
# mode:python
# End:
