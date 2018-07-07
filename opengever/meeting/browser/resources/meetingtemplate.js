(function(global, $, Controller) {

  "use strict";

  function MeetingTemplateController() {

    Controller.call(this);

    var self = this;
    var viewlet = $("#opengever_meeting_meetingtemplate");

    this.updateSortOrder = function() {
      var numbers = $.map($('.paragraphs-list li'), function(row) { return $(row).data().uid; });
      return $.post(viewlet.data().updateOrderUrl,
                    { sortOrder: JSON.stringify(numbers) }).fail(function() {
                      self.refresh();
                    });
    };

    this.events = [
      {
        method: "sortupdate",
        target: "#meetingtemplate_view .paragraphs-list",
        callback: this.updateSortOrder
      },
    ];

    this.onRender = function() {
      $('.paragraphs-list').sortable({
        items: "li",
        tolerance: "intersects",
        update: self.updateSortOrder
      });
      $(document).trigger("paragraphsReady");
    };

    this.init();

  }


  $(function() {

    if($("#opengever_meeting_meetingtemplate").length) {
      var controller = new MeetingTemplateController();
    }

  });

}(window, window.jQuery, window.Controller));
