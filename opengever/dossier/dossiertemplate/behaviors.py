from collective import dexteritytextindexer
from collective.elephantvocabulary import wrap_vocabulary
from opengever.base import _ as opengever_base_mf
from opengever.dossier import _
from opengever.dossier.behaviors.dossiernamefromtitle import DossierNameFromTitle
from plone.app.content.interfaces import INameFromTitle
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.i18n import MessageFactory as pd_mf  # noqa
from plone.directives import form
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IDossierTemplate(form.Schema):
    """Behaviour interface for dossier template types.

    Use this type of dossier to create a reusable template structures.
    """
    form.fieldset(
        u'common',
        label=opengever_base_mf(u'fieldset_common', default=u'Common'),
        fields=[
            u'keywords',
            u'comments',
        ],
    )

    form.order_after(keywords='IOpenGeverBase.description')
    dexteritytextindexer.searchable('keywords')
    keywords = schema.Tuple(
        title=_(u'label_keywords', default=u'Keywords'),
        description=_(u'help_keywords', default=u''),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
        default=(),
    )
    form.widget(keywords=TextLinesFieldWidget)

    form.order_after(comments='keywords')
    comments = schema.Text(
        title=_(u'label_comments', default=u'Comments'),
        required=False,
    )

    form.fieldset(
        u'filing',
        label=_(u'fieldset_filing', default=u'Filing'),
        fields=[
            u'filing_prefix',
        ],
    )

    filing_prefix = schema.Choice(
        title=_(u'filing_prefix', default="filing prefix"),
        source=wrap_vocabulary(
            'opengever.dossier.type_prefixes',
            visible_terms_from_registry="opengever.dossier"
            '.interfaces.IDossierContainerTypes.type_prefixes'),
        required=False,
    )

alsoProvides(IDossierTemplate, IFormFieldProvider)


class IDossierTemplateNameFromTitle(INameFromTitle):
    """Behavior interface.
    """


class DossierTemplateNameFromTitle(DossierNameFromTitle):
    """Choose IDs for a dossiertemplate in the following format:
    'dossiertemplate-{sequence number}'
    """

    implements(IDossierTemplateNameFromTitle)

    format = u'dossiertemplate-%i'
