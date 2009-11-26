from zope import schema
from zope.component import adapts
from zope.interface import implements, Interface

from plone.dexterity.interfaces import IDexterityContent
from plone.directives import form
from plone.app.dexterity.behaviors import metadata

from opengever.base import _


class ICreatorAware( Interface ):
    """ Marker Interface for ICreator behavior
    """


class ICreator( form.Schema ):

    form.omitted( 'creators' )
    creators = schema.Tuple(
        title = _( u'label_creators', u'Creators' ),
        description = _( u'help_creators', u'' ),
        value_type = schema.TextLine(),
        required = False,
        missing_value = (),
        )


class CreatorAware( object ):
    adapts( IDexterityContent )
    implements( ICreatorAware )

    creators = metadata.DCFieldProperty( ICreator['creators'],
                                         get_name = 'listCreators',
                                         set_name = 'setCreators' )

    def __init__( self, context ):
        self.context = context
        self.context.addCreator()

