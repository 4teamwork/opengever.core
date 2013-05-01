from z3c.saconfig import named_scoped_session
from zope.i18nmessageid import MessageFactory


Session = named_scoped_session("opengever")

_ = MessageFactory("opengever.globalindex")
