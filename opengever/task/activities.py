from opengever.ogds.base.actor import Actor
from opengever.task import _
from zope.i18n import translate


class TaskAddedDescription(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def kind(self):
        return _(u'task-added', default=u'Task added')

    @property
    def title(self):
        return self.context.title

    @property
    def summary(self):
        actor = Actor.lookup(self.context.Creator())
        msg = _('transition_label_created', 'Created by ${user}',
                mapping={'user': actor.get_label(with_principal=False)})
        return self.translate(msg)

    @property
    def description(self):
        msg = """<table>
            <tbody><tr>
              <th>Aufgabentitel</th>
              <td>Kennzahlen 2014 erarbeiten</td>
            </tr>
            <tr>
              <th>Dossiertitel</th>
              <td>Jahresdossier 2014</td>
            </tr>
            <tr>
              <th>Beschreibung</th>
              <td> simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.</td>
            </tr>
          </tbody></table>
"""
        return msg

    def translate(self, msg):
        return translate(msg, context=self.request)
