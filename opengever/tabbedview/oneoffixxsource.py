from ftw.table.basesource import BaseTableSource
from ftw.table.interfaces import ITableSource
from opengever.oneoffixx.browser.form import get_oneoffixx_templates
from opengever.tabbedview.interfaces import IOneoffixxTableSourceConfig
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(ITableSource)
@adapter(IOneoffixxTableSourceConfig, Interface)
class OneoffixxTableSource(BaseTableSource):
    """Base table source adapter for the OneOffixx."""

    searchable_columns = []

    def extend_query_with_textfilter(self, query, text):
        if text:
            if isinstance(text, str):
                text = text.decode('utf-8')
                query['filters'] = text.strip().split(' ')
        return query

    def search_results(self, query):
        filters = query.get('filters')

        templates = [
            {
                'title': template.title,
                'groupname': template.groupname,
                'content_type': template.content_type,
            }
            for template in get_oneoffixx_templates()
            if not filters or any(
                filter.lower() in template.title.lower()
                or filter.lower() in template.groupname.lower()
                for filter in filters
            )
        ]
        return templates
