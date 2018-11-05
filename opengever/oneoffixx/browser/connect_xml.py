from collections import OrderedDict
from lxml import etree
from opengever.dossier.interfaces import IDocProperties
from opengever.officeconnector.helpers import create_oc_url
from plone import api
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from zExceptions import NotFound
from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter


class OneoffixxConnectXml(BrowserView):

    def __call__(self):
        if not self.is_allowed():
            raise NotFound()

        self.settings = OrderedDict((
            ("KeepConnector", "true"),
            ("CreateConnectorResult", "true"),
            ("CreateConnectorResultOnError", "true"),
        ))

        self.commands = OrderedDict((
            ("DefaultProcess", (("start", "false"), )),
            ("ConvertToDocument", tuple()),
            ("SaveAs", (
                ("Overwrite", "true"),
                ("CreateFolder", "true"),
                ("AllowUpdateDocumentPart", "false"),
                ("Filename", ""),
            )),
            ("InvokeProcess", (
                ("Name", "OfficeConnector"),
                ("Arguments", create_oc_url(self.request, self.context, {"action": "checkout"})),
            )),
        ))

        self.document_properties = getMultiAdapter((self.context, self.request), IDocProperties).get_properties()

        self.request.RESPONSE.setHeader("Content-type", "application/xml")
        return self.generate_xml()

    def is_allowed(self):
        if api.content.get_state(self.context) == 'document-state-shadow':
            return True
        return False

    def generate_xml(self):
        nsmap = {None: "http://schema.oneoffixx.com/OneOffixxConnectBatch/1",
                 "xsi": "http://www.w3.org/2001/XMLSchema-instance"}
        batch = etree.Element("OneOffixxConnectBatch", nsmap=nsmap)
        batch.append(self.generate_settings_tag())

        entries = etree.SubElement(batch, "Entries")
        entries.append(self.generate_one_offixx_connect_tag())
        return etree.tostring(batch, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    def generate_settings_tag(self):
        settings_tag = etree.Element("Settings")
        for key, value in self.settings.iteritems():
            setting_tag = etree.SubElement(settings_tag, "Add")
            setting_tag.set("key", key)
            setting_tag.text = value
        return settings_tag

    @staticmethod
    def choose_language(languages):
        """ Templates can exist in several languages and we need
        to pick one. 2055 is for German Switzerland.
        """
        if 2055 in languages:
            return "2055"
        else:
            return str(languages[0])

    def generate_one_offixx_connect_tag(self):
        connect = etree.Element("OneOffixxConnect")
        arguments = etree.SubElement(connect, "Arguments")

        annotations = IAnnotations(self.context)
        if annotations.get('template-id'):
            template_id = etree.SubElement(arguments, "TemplateId")
            template_id.text = annotations['template-id']
        if annotations.get('languages'):
            language_id = etree.SubElement(arguments, "LanguageLcid")
            language = self.choose_language(annotations['languages'])
            language_id.text = language

        custom_interface = self.generate_custom_interface_connector_tag()
        connect.append(custom_interface)
        metadata = self.generate_metadata_tag()
        connect.append(metadata)
        commands = self.generate_commands_tag()
        connect.append(commands)
        return connect

    def generate_commands_tag(self):
        commands_tag = etree.Element("Commands")
        for command in self.commands:
            command_tag = etree.SubElement(commands_tag, "Command")
            command_tag.set("Name", command)
            parameters = self.commands[command]
            if not parameters:
                continue
            parameters_tag = etree.SubElement(command_tag, "Parameters")
            for key, value in parameters:
                parameter_tag = etree.SubElement(parameters_tag, "Add")
                parameter_tag.set("key", key)
                parameter_tag.text = value

        return commands_tag

    def generate_custom_interface_connector_tag(self):
        function = etree.Element("Function")
        function.set("name", "CustomInterfaceConnector")
        function.set("id", "70E94788-CE84-4460-9698-5663878A295B")

        arguments = etree.SubElement(function, "Arguments")

        interface = etree.SubElement(arguments, "Interface")
        interface.set("Name", "OneGovGEVER")

        for key, value in self.document_properties.items():
            node = etree.SubElement(interface, "Node")
            node.set("Id", key)
            if key in ('ogg.document.document_date',):
                value = api.portal.get_localized_time(value)
            if isinstance(value, basestring):
                node.text = safe_unicode(value)
            else:
                node.text = unicode(value)

        return function

    def generate_metadata_tag(self):
        function = etree.Element("Function")
        function.set("name", "MetaData")
        function.set("id", "c364b495-7176-4ce2-9f7c-e71f302b8096")

        for key, value in self.document_properties.items():
            node = etree.SubElement(function, "Value")
            node.set("key", key)
            node.set("type", "string")
            if key in ('ogg.document.document_date',):
                value = api.portal.get_localized_time(value)
            if isinstance(value, basestring):
                node.text = safe_unicode(value)
            else:
                node.text = unicode(value)

        return function
