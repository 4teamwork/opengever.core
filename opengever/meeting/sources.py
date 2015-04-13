from plone.formwidget.contenttree import ObjPathSourceBinder


sablon_template_source = ObjPathSourceBinder(
    portal_type=("opengever.meeting.sablontemplate"),
    navigation_tree_query={
        'object_provides':
            ['opengever.dossier.templatedossier.interfaces.ITemplateDossier',
             'opengever.meeting.sablontemplate.ISablonTemplate',
             ],
        }
)
