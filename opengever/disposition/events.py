from plone import api


def handle_evaluation_finalize(context, event):
    if not context.responsible and event.action == 'disposition-transition-appraise':
        context.responsible = api.user.get_current().id
