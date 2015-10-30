(function(global, $) {

  "use strict";

  $(function() {

    // autosizing textareas when add or editing a proposal
    $('body.template-opengever-meeting-proposal textarea').autosize();
    $('body.template-edit.portaltype-opengever-meeting-proposal textarea').autosize();

    var viewlet = $("#opengever_meeting_meeting");

    var messageFactory = new global.MessageFactory(viewlet);

  });

}(window, jQuery));
