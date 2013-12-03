from plone.app.versioningbehavior.behaviors import IVersionable
from plone.autoform.interfaces import OMITTED_KEY
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.model import Fieldset
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IEditForm
from zope.interface import Interface


# Note: the changeNote field from the IVersionable behavior is being dropped
# and moved in this file to avoid setting the tagged values too early
# (document.py gets imported in many places, to get the IDocumentSchema for
# example) and running into load order issues. So this part will be executed
# whenever opengever.document is being grokked.


# move the changeNote to the 'common' fieldset

IVersionable.setTaggedValue(FIELDSETS_KEY, [
        Fieldset('common', fields=[
                'changeNote',
                ])
        ])

# omit the changeNote from all forms because it's not possible to create a new
# version when editing document metadata

IVersionable.setTaggedValue(OMITTED_KEY, [
    (Interface, 'changeNote', 'true'),
    (IEditForm, 'changeNote', 'true'),
    (IAddForm, 'changeNote', 'true'),])
