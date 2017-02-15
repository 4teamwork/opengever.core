diff --git a/opengever/policy/base/upgrades/20160923114424_install_opengever_private/upgrade.py b/opengever/policy/base/upgrades/20160923114424_install_opengever_private/upgrade.py
index defa14a..11ce634 100644
--- a/opengever/policy/base/upgrades/20160923114424_install_opengever_private/upgrade.py
+++ b/opengever/policy/base/upgrades/20160923114424_install_opengever_private/upgrade.py
@@ -11,6 +11,9 @@ class InstallOpengeverPrivate(UpgradeStep):
 
     def __call__(self):
         self.install_upgrade_profile()
+        mtool = api.portal.get_tool('portal_membership')
+        mtool.setMembersFolderById(MEMBERSFOLDER_ID)
+        mtool.setMemberAreaType('opengever.private.folder')
         if not api.portal.get().get(MEMBERSFOLDER_ID):
             self.create_private_root()
 
