from datetime import date
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_true(context):
    return True


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_42(context):
    return 42


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_fr(context):
    return u'fr'


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_some_text(context):
    return u'Some text'


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_some_text_line(context):
    return u'Some text line'


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_gruen(context):
    return set([u'gr\xfcn'])


@provider(IContextAwareDefaultFactory)
def dummy_default_factory_today(context):
    return date.today()
