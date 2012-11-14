from zope.component import adapts
from zope.interface import implements, Interface
from ftw.tooltip.interfaces import ITooltipSource


class OpengeverTabbedviewTooltipSource(object):
    """Opengever Tabbedview Tooltip Source.
    Used for example in all document listings."""

    implements(ITooltipSource)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def global_condition(self):
        return True

    def tooltips(self):
        return [{
            'selector': u'.tabbedview-tooltip',
            'condition': '#documents_overview, #mydocuments_overview, ' \
                         '#relateddocuments_overview',
            'content': u'.tabbedview-tooltip-data',
        }]
