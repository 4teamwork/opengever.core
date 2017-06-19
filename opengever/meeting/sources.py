from plone.formwidget.contenttree import ObjPathSourceBinder


sablon_template_source = ObjPathSourceBinder(
    portal_type=("opengever.meeting.sablontemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatefolder.interfaces.ITemplateFolder',
             'opengever.meeting.sablontemplate.ISablonTemplate',
             ],
        }
)
