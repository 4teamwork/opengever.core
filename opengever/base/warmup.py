from ftw.monitor.interfaces import IWarmupPerformer
from ftw.monitor.warmup import DefaultWarmupPerformer
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IWarmupPerformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class GEVERWarmupPerformer(DefaultWarmupPerformer):
    """Extends DefaultWarmupPerformer from ftw.monitor with 'trashed' index.
    """

    WARMUP_INDEXES = DefaultWarmupPerformer.WARMUP_INDEXES + ['trashed']
