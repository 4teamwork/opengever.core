from plonetheme.teamraum import _
from plonetheme.teamraum.importexport import CSS_PREFIX
from plonetheme.teamraum.importexport import CustomStylesUtility
from plonetheme.teamraum.importexport import LOGO_KEY
from plonetheme.teamraum.importexport import LOGO_RIGHT_KEY
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zope.i18n import translate
from zope.publisher.browser import BrowserView
import json


class TeamraumThemeControlpanel(BrowserView):

    def __call__(self):
        customstyles_util = CustomStylesUtility(self.portal)
        # reset styles if there is nothing in annotations
        if 'customstyles' not in customstyles_util.annotations:
            customstyles_util.reset_styles()

        if self.request.form.get('form.submitted', None):
            items = self.request.form
            customstyles_util.save_styles(items)
            IStatusMessage(self.request).addStatusMessage(
                _(u'info_changes_saved',
                  default=u'Changes saved'), type='info')

        if self.request.form.get('form.export', None):
            self.context.REQUEST.RESPONSE.setHeader(
                'Content-Type',
                'text/json; charset=utf-8')
            self.context.REQUEST.RESPONSE.setHeader(
                'Content-disposition',
                'attachment; filename=customstyles.json')
            return customstyles_util.export_styles()

        if self.request.form.get('form.import', None):
            upload = self.request.form.get('import_styles', None)
            if upload:
                customstyles_util.import_styles(json.loads(upload.read()))

        if self.request.form.get('form.reset', None):
            customstyles_util.reset_styles()
            IStatusMessage(self.request).addStatusMessage(
                _(u'info_changes_resetted',
                  default=u'Changes resetted'), type='info')

        if self.request.form.get('reset_logo', None):
            customstyles_util.reset_logo()
            IStatusMessage(self.request).addStatusMessage(
                _(u'info_logo_resetted',
                  default=u'Logo resetted'), type='info')
            self.request.response.redirect('@@%s' % self.__name__)

        if self.request.form.get('reset_logo_right', None):
            customstyles_util.reset_logo_right()
            IStatusMessage(self.request).addStatusMessage(
                _(u'info_logo_resetted',
                  default=u'Logo resetted'), type='info')
            self.request.response.redirect('@@%s' % self.__name__)
        return self.index()

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    def defaults(self):
        customstyles_util = CustomStylesUtility(self.portal)
        return customstyles_util.defaults

    def has_right_logo(self):
        customstyles_util = CustomStylesUtility(self.portal)
        if LOGO_RIGHT_KEY in customstyles_util.annotations['customstyles']:
            if customstyles_util.annotations['customstyles'][LOGO_RIGHT_KEY]:
                return True
        return False

    def logo_right_url(self):
        customstyles_util = CustomStylesUtility(self.portal)
        if LOGO_RIGHT_KEY in customstyles_util.annotations['customstyles']:
            if customstyles_util.annotations['customstyles'][LOGO_RIGHT_KEY]:
                return "%s/customlogoright" % self.portal.absolute_url()
        return "%s/++theme++plonetheme.teamraum/images/logo_teamraum.png" % \
            self.portal.absolute_url()

    def logo_url(self):
        customstyles_util = CustomStylesUtility(self.portal)
        if LOGO_KEY in customstyles_util.annotations['customstyles']:
            if customstyles_util.annotations['customstyles'][LOGO_KEY]:
                return "%s/customlogo" % self.portal.absolute_url()
        return "%s/++theme++plonetheme.teamraum/images/logo_teamraum.png" % \
            self.portal.absolute_url()

    def customfield(self, fieldid, label, cssclass="", help=""):
        """Creates a field and returns its html code.
        """
        customstyles_util = CustomStylesUtility(self.portal)
        default = ''
        field_key = '%s%s' % (CSS_PREFIX, fieldid)
        if field_key in customstyles_util.defaults:
            default = customstyles_util.defaults[field_key]
        afterfield = ''
        if cssclass == 'colorSelection':
            afterfield = """<input type="button"
         class="pickColorButton"
         style="background-color:%s"
         value=""
         />
""" % default
        translated_label = translate(
            label, domain='plonetheme.teamraum', context=self.request)
        translated_help = translate(
            help, domain='plonetheme.teamraum', context=self.request)

        return """
<div class="field">
  <label for="css_%(fieldid)s">%(label)s</label>
  <div class="formHelp">%(help)s</div>
  <input type="text"
         name="%(field_key)s"
         id="css_%(fieldid)s"
         class="%(cssclass)s"
         value="%(default)s"
         />%(afterfield)s
</div>
""" % {'fieldid': fieldid,
       'field_key': field_key,
       'label': translated_label,
       'default': default,
       'help': translated_help,
       'afterfield': afterfield,
       'cssclass': cssclass}
