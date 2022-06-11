""" Resolves the javascript dependency graph
Run this script to linearize the dependency graph for
all javascript dependencies in opengever.base and opengever.meeting

The output of the script will be a list of all dependencies in a
linear order.
Put these dependencies in the javascript registry.
When adding additional javascript files put the dependencies
in this file and recalculate the graph.

The dependencies are defined like this:

{
    '*module1*': ['*dependency1*'], ['*dependency2*']...,
    '*module2*': ['*dependency1*'], ['*dependency2*']...,
    ...
}
"""

from tarjan import tarjan


graph = {
    'controller': ['handlebars', 'messagefactory', 'jquery'],
    'messagefactory': ['jquery', 'notify'],
    'storage': ['jquery', 'messagefactory'],
    'meetingstorage': ['jquery', 'storage'],
    'synchronizer': ['jquery'],
    'livesearch': ['jquery'],
    'quickupload': ['jquery'],
    'notify': ['jquery'],
    'qtip': ['jquery'],
    'autocomplete': ['jquery'],
    'tooltip': ['jquery', 'qtip'],
    'trixcustom': ['trix'],
    'trix': [],
    'base': ['jquery'],
    'datetimepicker_base': ['jquery'],
    'datetimepicker_meeting': ['jquery', 'datetimepicker_base'],
    'handlebars': [],
    'editbox': ['jquery', 'controller'],
    'editor': ['jquery', 'handlebars', 'controller', 'meetingstorage', 'synchronizer'],
    'meeting': ['jquery', 'controller', 'editbox', 'pin'],
    'protocol': ['jquery', 'meetingstorage', 'pin', 'synchronizer', 'controller', 'scrollspy', 'autocomplete'],
    'scrollspy': ['jquery'],
    'pin': ['jquery'],
    'prepoverlay': ['jquery'],
    'ajax-prefilter': ['jquery'],
    'breadcrumbs': ['jquery'],
}

print tarjan(graph)
