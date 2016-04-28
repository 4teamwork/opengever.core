from opengever.base.monkey.patching import MonkeyPatch


class PatchCreateMailInContainer(MonkeyPatch):
    """Patch ftw.mail.inbound.createMailInContainer

    Because `preserved_as_paper` has a schema level default, its default
    value doesn't get set correctly, so we set explicitely after setting the
    defaults.

    XXX: Fix in ftw.mail and remove this monkey patch
    """

    def __call__(self):

        from AccessControl import getSecurityManager
        from AccessControl import Unauthorized
        from Acquisition import aq_inner
        from ftw.mail.inbound import set_defaults
        from opengever.document.interfaces import IDocumentSettings
        from plone.dexterity.interfaces import IDexterityFTI
        from plone.dexterity.utils import createContent
        from plone.i18n.normalizer.interfaces import IIDNormalizer
        from plone.registry.interfaces import IRegistry
        from zope.component import getUtility
        from zope.component import queryUtility
        from zope.container.interfaces import INameChooser
        from zope.schema import getFields
        from zope.security.interfaces import IPermission

        def createMailInContainer(container, message):
            """Add a mail object to a container.

            The new object, wrapped in its new acquisition context, is
            returned.
            """
            # lookup the type of the 'message' field and create an instance
            fti = getUtility(IDexterityFTI, name='ftw.mail.mail')
            schema = fti.lookupSchema()
            field_type = getFields(schema)['message']._type
            message_value = field_type(
                data=message,
                contentType='message/rfc822',
                filename=u'message.eml')
            # create mail object
            content = createContent('ftw.mail.mail', message=message_value)

            container = aq_inner(container)
            container_fti = container.getTypeInfo()

            # check permission
            permission = queryUtility(
                IPermission, name='ftw.mail.AddInboundMail')
            if permission is None:
                raise Unauthorized("Cannot create %s" % content.portal_type)
            if not getSecurityManager().checkPermission(
                    permission.title, container):
                raise Unauthorized("Cannot create %s" % content.portal_type)

            # check addable types
            if container_fti is not None and \
                    not container_fti.allowType(content.portal_type):
                raise ValueError("Disallowed subobject type: %s" % (
                    content.portal_type))

            normalizer = queryUtility(IIDNormalizer)
            normalized_subject = normalizer.normalize(content.title)

            name = INameChooser(container).chooseName(
                normalized_subject, content)
            content.id = name

            new_name = container._setObject(name, content)
            obj = container._getOb(new_name)
            obj = set_defaults(obj, container)

            # ---- patched
            registry = getUtility(IRegistry)
            document_settings = registry.forInterface(IDocumentSettings)
            preserved = document_settings.preserved_as_paper_default
            obj.preserved_as_paper = preserved
            # ---- patched

            obj.reindexObject()
            return obj

        from ftw.mail import inbound
        self.patch_refs(inbound, 'createMailInContainer', createMailInContainer)
