from BTrees.OOBTree import OOBTree
from plone.app.blob.field import BlobWrapper, ReuseBlob
from plone.app.blob.interfaces import IBlobbable
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from zope.annotation.interfaces import IAnnotations
import base64
import copy
import json


LOGO_KEY = 'css.logo'
LOGO_RIGHT_KEY = 'css.logo_right'
LOGO_TITLE_KEY = 'css.logo_title'
CSS_PREFIX = 'css.'

DEFAULT_STYLES = {
    u'css.additional_css': u'',
    u'css.content_background': u'#FFFFFF',
    u'css.content_width': u'90%',
    u'css.font_size': u'12px',
    u'css.footer_background': u'#f8f8f8',
    u'css.footer_height': u'',
    u'css.gnav_active_end': u'#3387a1',
    u'css.gnav_active_shadowinset': u'#3997b4',
    u'css.gnav_active_shadowtop': u'#4a555b',
    u'css.gnav_active_start': u'#3387a1',
    u'css.gnav_grad_end': u'#4a555b',
    u'css.gnav_grad_start': u'#70777d',
    u'css.gnav_hover_end': u'#7c848a',
    u'css.gnav_hover_shadowinset': u'#787f86',
    u'css.gnav_hover_shadowtop': u'#4a555b',
    u'css.gnav_hover_start': u'#7c848a',
    u'css.gnav_shadowinset': u'#787f86',
    u'css.gnav_shadowtop': u'#4a555b',
    u'css.header_background': u'#FFFFFF',
    u'css.header_height': u'60px',
    u'css.headerbox_background': u'rgba(255,255,255,0.6)',
    u'css.headerbox_spacetop': u'1em',
    u'css.link_color': u'#205C90',
    u'css.login_background': u'#3387a1',
    u'css.logo_spaceleft': u'on',
    u'css.logo_title': u'',
    # u'css.logo': u'<base64>',
    u'css.text_color': u'#444',
}


class CustomStylesUtility(object):
    """This utility is in charge of handling import and export of custom
    styles. It is used by the setuphandlers and the controlpanel.
    """

    def __init__(self, context):
        self.context = context

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def annotations(self):
        return IAnnotations(self.portal)

    @property
    def portal_css(self):
        return getToolByName(self.context, 'portal_css')

    @property
    def defaults(self):
        return self.annotations.get('customstyles', OOBTree(DEFAULT_STYLES))

    def reset_styles(self):
        """Reset the custom styles to defaults.
        """
        self.annotations['customstyles'] = OOBTree(DEFAULT_STYLES)

    def reset_logo_right(self):
        """Reset the custom styles logo on the right side.
        """
        if LOGO_RIGHT_KEY in self.annotations['customstyles']:
            del self.annotations['customstyles'][LOGO_RIGHT_KEY]
            # TODO: save_styles to recalculate the logo padding...

    def reset_logo(self):
        """Reset the custom styles logo.
        """
        if LOGO_KEY in self.annotations['customstyles']:
            del self.annotations['customstyles'][LOGO_KEY]
            # TODO: save_styles to recalculate the logo padding...

    def get_logo_right(self, logo_file):
        """ Read the logo from a file-like stream object `logo_file` and create
        a blob from it, or resuse the existing one if none has been uploaded.
        """
        logo, blob = None, None
        data = logo_file.read()
        if data:
            blob = BlobWrapper('image/png')
            if isinstance(data, basestring):
                value = StringIO(data)
                if value is not None:
                    blobbable = IBlobbable(value)
                    try:
                        blobbable.feed(blob.getBlob())
                    except ReuseBlob, exception:
                        blob.setBlob(exception.args[0])
            blob.setFilename(blobbable.filename())
        if blob:
            logo = blob
        elif LOGO_RIGHT_KEY in self.annotations['customstyles']:
            # use existing logo if none is uploaded
            logo = self.annotations['customstyles'][LOGO_RIGHT_KEY]
        return logo

    def get_logo(self, logo_file):
        """ Read the logo from a file-like stream object `logo_file` and create
        a blob from it, or resuse the existing one if none has been uploaded.
        """
        logo, blob = None, None
        data = logo_file.read()
        if data:
            blob = BlobWrapper('image/png')
            if isinstance(data, basestring):
                value = StringIO(data)
                if value is not None:
                    blobbable = IBlobbable(value)
                    try:
                        blobbable.feed(blob.getBlob())
                    except ReuseBlob, exception:
                        blob.setBlob(exception.args[0])
            blob.setFilename(blobbable.filename())
        if blob:
            logo = blob
        elif LOGO_KEY in self.annotations['customstyles']:
            # use existing logo if none is uploaded
            logo = self.annotations['customstyles'][LOGO_KEY]
        return logo

    def save_styles(self, items):
        """Saves the styles passed in as items to annotations.
        """
        styles = {}
        for key, value in items.items():
            if key == LOGO_KEY:
                logo = self.get_logo(value)
                styles[LOGO_KEY] = logo
            elif key == LOGO_RIGHT_KEY and value:
                logo_right = self.get_logo_right(value)
                styles[LOGO_RIGHT_KEY] = logo_right
            elif key == LOGO_TITLE_KEY:
                if isinstance(value, unicode):
                    value = value.encode('utf8')
                styles[key] = value.decode('utf8')
            elif key.startswith(CSS_PREFIX):
                styles[key] = value

        self.annotations['customstyles'] = OOBTree(styles)
        # TODO: save theme settings
        # applyTheme(None)
        self.portal_css.cookResources()

    def export_styles(self):
        """Returns a json file containing the styles.
        """
        styles = copy.deepcopy(self.annotations['customstyles'])

        if LOGO_KEY in styles:
            # copy blob directly from annotations
            styles[LOGO_KEY] = base64.b64encode(
                self.annotations['customstyles'][LOGO_KEY].data)

        if LOGO_RIGHT_KEY in styles and styles[LOGO_RIGHT_KEY]:
            # copy blob directly from annotations
            styles[LOGO_RIGHT_KEY] = base64.b64encode(
                self.annotations['customstyles'][LOGO_RIGHT_KEY].data)

        return json.dumps(dict(styles))

    def import_styles(self, styles):
        """Imports styles to annotations.
        """
        if LOGO_KEY in styles:
            styles[LOGO_KEY] = StringIO(
                base64.b64decode(styles[LOGO_KEY]))

        if LOGO_RIGHT_KEY in styles and styles[LOGO_RIGHT_KEY]:
            styles[LOGO_RIGHT_KEY] = StringIO(
                base64.b64decode(styles[LOGO_RIGHT_KEY]))

        self.save_styles(styles)
