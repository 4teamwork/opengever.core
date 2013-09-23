## Script (Python) "livescript_reply"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=q,limit=10,path=None
##title=Determine whether to show an id in an edit form

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.PythonScripts.standard import url_quote
from Products.PythonScripts.standard import url_quote_plus
from Products.PythonScripts.standard import html_quote


ploneUtils = getToolByName(context, 'plone_utils')
portal_url = getToolByName(context, 'portal_url')()
pretty_title_or_id = ploneUtils.pretty_title_or_id
plone_view = context.restrictedTraverse('@@plone')
portal_state = context.restrictedTraverse('@@plone_portal_state')

portalProperties = getToolByName(context, 'portal_properties')
siteProperties = getattr(portalProperties, 'site_properties', None)
useViewAction = []
if siteProperties is not None:
    useViewAction = siteProperties.getProperty('typesUseViewActionInListings', [])

# SIMPLE CONFIGURATION
USE_ICON = True
USE_RANKING = False
MAX_TITLE = 29
MAX_DESCRIPTION = 93

# generate a result set for the query
catalog = context.portal_catalog

friendly_types = ploneUtils.getUserFriendlyTypes()

# multi language support
ltool = getToolByName(context, 'portal_languages')
lang_title = 'title_%s' % ltool.getPreferredLanguage()

def quotestring(s):
    return '"%s"' % s

def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

# for now we just do a full search to prove a point, this is not the
# way to do this in the future, we'd use a in-memory probability based
# result set.
# convert queries to zctextindex

# XXX really if it contains + * ? or -
# it will not be right since the catalog ignores all non-word
# characters equally like
# so we don't even attept to make that right.
# But we strip these and these so that the catalog does
# not interpret them as metachars
##q = re.compile(r'[\*\?\-\+]+').sub(' ', q)
for char in '?-+*':
    q = q.replace(char, ' ')
r=q.split()
r = " AND ".join(r)
r = quote_bad_chars(r)+'*'
searchterms = url_quote_plus(r)

site_encoding = context.plone_utils.getSiteEncoding()
if path is None:
    path = getNavigationRoot(context)
results = catalog(SearchableText=r, portal_type=friendly_types, path=path)

searchterm_query = '?searchterm=%s'%url_quote_plus(q)

RESPONSE = context.REQUEST.RESPONSE
RESPONSE.setHeader('Content-Type', 'text/xml;charset=%s' % site_encoding)

# replace named entities with their numbered counterparts, in the xml the named ones are not correct
#   &darr;      --> &#8595;
#   &hellip;    --> &#8230;
legend_livesearch = _('legend_livesearch', default='LiveSearch &#8595;')
label_no_results_found = _('label_no_results_found', default='No matching results found.')
label_advanced_search = _('label_advanced_search', default='Advanced Search&#8230;')
label_show_all = _('label_show_all', default='Show all&#8230;')

output = []

def write(s):
    output.append(safe_unicode(s))

if not results:
    write('''<fieldset class="livesearchContainer">''')
    write('''<legend id="livesearchLegend">%s</legend>''' % context.translate(legend_livesearch))
    write('''<div class="LSIEFix">''')
    write('''<div id="LSNothingFound">%s</div>''' % context.translate(label_no_results_found))
    write('''<div class="LSRow">''')
    write('<a href="advanced_search" style="font-weight:normal">%s</a>' % context.translate(label_advanced_search))
    write('''</div>''')
    write('''</div>''')
    write('''</fieldset>''')

else:

    write('''<fieldset class="livesearchContainer">''')
    write('''<legend id="livesearchLegend">%s</legend>''' % context.translate(legend_livesearch))
    write('''<div class="LSIEFix">''')
    write('''<ul class="LSTable">''')
    for result in results[:limit]:
        itemUrl = result.getURL()
        if result.portal_type in useViewAction:
            itemUrl += '/view'
        itemUrl = itemUrl + searchterm_query

        write('''<li class="LSRow">''')
        full_title = getattr(result, lang_title, None)
        if full_title:
            full_title = safe_unicode(full_title)
        else:
            full_title = safe_unicode(pretty_title_or_id(result))
        if len(full_title) > MAX_TITLE:
            display_title = ''.join((full_title[:MAX_TITLE],'...'))
        else:
            display_title = full_title
        full_title = full_title.replace('"', '&quot;')
        icon_class = 'contenttype-%s' % (ploneUtils.normalizeString(result.portal_type))
        write('''<a href="%s" class="%s" title="%s">%s</a>''' % (itemUrl, icon_class, full_title, display_title))
        write('''<span class="discreet" dir="%s">[%s%%]</span>''' % (test(portal_state.is_rtl(), 'rtl', 'ltr'), result.data_record_normalized_score_))
        display_description = safe_unicode(result.Description or '')
        if len(display_description) > MAX_DESCRIPTION:
            display_description = ''.join((display_description[:MAX_DESCRIPTION],'...'))
        # need to quote it, to avoid injection of html containing javascript and other evil stuff
        display_description = html_quote(display_description)
        write('''<div class="LSDescr">%s</div>''' % (display_description))
        write('''</li>''')
        full_title, display_title, display_description = None, None, None

    write('''<li class="LSRow">''')
    write( '<a href="advanced_search" style="font-weight:normal">%s</a>' % context.translate(label_advanced_search, domain="izug.basetheme"))
    write('''</li>''')

    if len(results)>limit:
        # add a more... row
        write('''<li class="LSRow">''')
        write( '<a href="%s" style="font-weight:normal">%s</a>' % ('search?SearchableText=' + searchterms, context.translate(label_show_all, domain="izug.basetheme")))
        write('''</li>''')
    write('''</ul>''')
    write('''</div>''')
    write('''</fieldset>''')

return '\n'.join(output).encode(site_encoding)
