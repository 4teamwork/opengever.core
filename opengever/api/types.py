from opengever.base.interfaces import IOpengeverBaseLayer
from opengever.locking.utils import has_move_lock
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services.types.get import check_security
from plone.restapi.services.types.get import TypesInfo
from plone.restapi.services.types.get import TypesGet
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.interfaces import IPublishTraverse


@implementer(IExpandableElement)
@adapter(Interface, IOpengeverBaseLayer)
class TypesInfo(TypesInfo):

    def __call__(self, expand=False):
        result = {"types": {"@id": "{}/@types".format(self.context.absolute_url())}}
        if not expand:
            return result

        check_security(self.context)

        vocab_factory = getUtility(
            IVocabularyFactory, name="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )

        portal_types = getToolByName(self.context, "portal_types")

        # allowedContentTypes already checks for permissions
        allowed_types = [x.getId() for x in self.context.allowedContentTypes()]

        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()

        # only addables if the content type is folderish
        can_add = IFolderish.providedBy(self.context) and not has_move_lock(self.context)

        # Filter out any type that doesn't have lookupSchema. We are depended
        # on that in lower level code.
        ftis = [portal_types[x.value] for x in vocab_factory(self.context)]
        ftis = [fti for fti in ftis if getattr(fti, "lookupSchema", None)]

        result["types"] = [
            {
                "@id": "{}/@types/{}".format(portal_url, fti.getId()),
                "title": translate(fti.Title(), context=self.request),
                "addable": fti.getId() in allowed_types if can_add else False,
            }
            for fti in ftis
        ]

        return result


@implementer(IPublishTraverse)
class TypesGet(TypesGet):
    def reply(self):
        if not self.params:
            # List type info, including addable_types
            info = TypesInfo(self.context, self.request)
            return info(expand=True)["types"]

        if len(self.params) == 1:
            return self.reply_for_type()

        if len(self.params) == 2:
            return self.reply_for_field()
