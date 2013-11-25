from five import grok
from ZODB.POSException import ConflictError
from zope.interface import Interface


class IsPastingAllowedView(grok.View):
    """A view to determine if pasting objects is supposed to be allowed on a
    particular context.
    Used in the available expression of the object_buttons 'paste' action.
    """

    grok.name('is_pasting_allowed')
    grok.context(Interface)
    grok.require('zope2.View')

    disabled_types = ('opengever.dossier.templatedossier',
                      'opengever.contact.contactfolder')

    def render(self):
        valid_cb_data = False
        try:
            valid_cb_data = self.context.cb_dataValid()
        except (ConflictError, KeyboardInterrupt, SystemExit):
            raise
        except:
            pass

        pasting_allowed = valid_cb_data and \
            self.context.portal_type not in self.disabled_types

        return pasting_allowed
