from ftw.keywordwidget.vocabularies import KeywordSearchableSource
from ftw.keywordwidget.vocabularies import KeywordWidgetAddableSourceWrapper
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IContextSourceBinder


class IRestrictKeywords(Interface):
    """Marker interface for restricting the keyword vocabulary"""


class KeywordWidgetAddableRestrictableSourceWrapper(KeywordWidgetAddableSourceWrapper):

    def __init__(self, source, restricted, allowed_terms):
        super(KeywordWidgetAddableRestrictableSourceWrapper, self).__init__(source)
        self.restricted = restricted
        self.allowed_terms = allowed_terms

    def search(self, query_string):
        q = query_string.lower()
        if self.restricted:
            return [self.getTerm(kw) for kw in self.allowed_terms if q in kw.lower()]
        return self._source.search(query_string)

    def __iter__(self):
        if self.restricted:
            return iter(self.getTerm(kw) for kw in self.allowed_terms)
        return iter(self._source)


@implementer(IContextSourceBinder)
class KeywordAddableRestrictableSourceBinder(object):

    def __call__(self, context):
        request = context.REQUEST
        restricted = IRestrictKeywords.providedBy(request)
        allowed_terms = getattr(request, 'allowed_keywords', [])
        return KeywordWidgetAddableRestrictableSourceWrapper(
            KeywordSearchableSource(context),
            restricted,
            allowed_terms)
