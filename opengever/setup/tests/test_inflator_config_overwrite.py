from lxml import etree
from pkg_resources import resource_filename
from unittest import TestCase


NAMESPACES = {'genericsetup': 'http://namespaces.zope.org/genericsetup', }
XPATH_GEVER = "//genericsetup:importStep[@name='ftw.inflator.content_creation']"
XPATH_DEPENDS = "//*[local-name() = 'depends'][@name='opengever.setup.unit_creation']"
XPATH_INFLATOR = "//genericsetup:importStep"


def xpath(node, xpath):
    return node.xpath(xpath, namespaces=NAMESPACES)[0]


class TestInflatorConfig(TestCase):

    maxDiff = None
    longMessage = True

    def test_inflator_config_correctly_overwritten(self):
        parser = etree.XMLParser(remove_blank_text=True)

        inflator_path = resource_filename(
            'ftw.inflator.creation', 'configure.zcml')
        inflator_config = etree.parse(inflator_path, parser)
        inflator_setup = xpath(inflator_config, XPATH_INFLATOR)

        gever_path = resource_filename(
            'opengever.setup.creation', 'configure.zcml')
        gever_config = etree.parse(gever_path, parser)
        gever_setup = xpath(gever_config, XPATH_GEVER)
        additional_element = xpath(gever_config, XPATH_DEPENDS)
        additional_element.getparent().remove(additional_element)

        self.assertMultiLineEqual(
            etree.tostring(inflator_setup, pretty_print=True),
            etree.tostring(gever_setup, pretty_print=True),

            "Gever's overwritten inflator config in "
            "'opengever.setup.creation.configure.zcml' and ftw.inflator's "
            "config in 'ftw.inflator.creation.configure.zcml' are different. "
            "Maybe new changes from 'ftw.inflator' need to be updated in "
            "the overwritten config file?")
