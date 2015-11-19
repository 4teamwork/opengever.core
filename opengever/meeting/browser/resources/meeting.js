(function(global, $) {

  "use strict";

  $(function() {

    // autosizing textareas when add or editing a proposal
    global.autosize($('body.template-opengever-meeting-proposal textarea'));
    global.autosize($('body.template-edit.portaltype-opengever-meeting-proposal textarea'));

    var viewlet = $("#opengever_meeting_meeting");

    var messageFactory = new global.MessageFactory(viewlet);

  });

}(window, jQuery));
