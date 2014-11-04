from OFS.ObjectManager import ObjectManager

ADD_PLONE_SITE_HTML = '''
<dtml-if "_.len(this().getPhysicalPath()) == 1 or this().meta_type == 'Folder' and 'PloneSite' not in [o.__class__.__name__ for o in this().aq_chain]">
  <!-- Add opengever client site action-->
  <form method="get"
        action="&dtml-URL1;/@@gever-add-deployment"
        style="text-align: right; margin-top:0.5em; margin-bottom:0em;"
        target="_top">
    <input type="submit" value="Install OneGov GEVER" />
  </form>
</dtml-if>

<dtml-if "this().meta_type == 'Plone Site'">
  <!-- Warn if outdated -->
  <dtml-if "this().portal_setup.listUpgrades('opengever.policy.base:default') != []">
    <div style="background: #CC2A2A; padding: 10px; font-weight: bold; font-size: 125%;
                margin-top: 1em;">
      This OpenGever client's configuration is outdated and needs to be upgraded.
      <a href="&dtml-URL1;/portal_setup/manage_upgrades?profile_id=opengever.policy.base:default" title="Go to the upgrade page">
        Please continue with the upgrade.
      </a>
    </div>
  </dtml-if>
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
