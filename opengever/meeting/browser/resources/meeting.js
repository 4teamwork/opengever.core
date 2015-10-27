(function(global, $) {

  "use strict";

  $(function() {

    // autosizing textareas when add or editing a proposal
    $('body.template-opengever-meeting-proposal textarea').autosize();
    $('body.template-edit.portaltype-opengever-meeting-proposal textarea').autosize();

    var viewlet = $("#opengever_meeting_meeting");

    var messageFactory = new global.MessageFactory(viewlet);

    var onUpdateSuccess = function(data) { messageFactory.shout(data.messages); };

    var onUpdateFail = function(data) { messageFactory.shout(JSON.parse(data.responseText).messages); };

    var updateAgendaItem = function(title) {
      var id = this.trigger.data().id;
      var payload = { agenda_item_id: id, title: title };
      return $.ajax({
        method: "POST",
        dataType: "json",
        contentType: "application/json",
        url: viewlet.data("update-agenda-item-url"),
        data: payload
      }).done(onUpdateSuccess).fail(onUpdateFail);
    };

    var agendaItemTitleValidator = function(data) { return data.proceed; };

    $("#agenda_items tr").each(function() {
      var source;
      if($(".title > span > a", this).length) {
        source = $(".title > span > a", this);
      } else {
        source = $(".title > span", this);
      }
      var editbox = new global.Editbox({
        trigger: $(".edit_agenda_item", this),
        editbox: $(".title .edit_box", this),
        source: source,
        onChange: updateAgendaItem,
        responseValidator: agendaItemTitleValidator
      });
    });

  });

}(window, jQuery));
