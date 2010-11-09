from OFS.ObjectManager import ObjectManager

ADD_PLONE_SITE_HTML = '''
<dtml-if "_.len(this().getPhysicalPath()) == 1 or this().meta_type == 'Folder' and 'PloneSite' not in [o.__class__.__name__ for o in this().aq_chain]">
  <!-- Add opengever client site action-->
  <form method="get"
        action="&dtml-URL1;/@@opengever-addclient"
        style="text-align: right; margin-top:0.5em; margin-bottom:0em;"
        target="_top">
    <input type="hidden" name="site_id" value="Plone" />
    <input type="submit" value="Install Opengever" />
  </form>
</dtml-if>
'''

main = ObjectManager.manage_main
orig = main.read()
pos = orig.find('<!-- Add object widget -->')

# Add in our button html at the right position
new = orig[:pos] + ADD_PLONE_SITE_HTML + orig[pos:]

# Modify the manage_main
main.edited_source = new
main._v_cooked = main.cook()
