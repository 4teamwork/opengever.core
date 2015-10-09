(function(global, $) {

  "use strict";

  $(function() {

    // autosizing textareas when add or editing a proposal
    $('body.template-opengever-meeting-proposal textarea').autosize();
    $('body.template-edit.portaltype-opengever-meeting-proposal textarea').autosize();

    var viewlet = $("#opengever_meeting_meeting");

    var messageFactory = new global.MessageFactory(viewlet);

    var toggleAttachements = function() {
      $(this).parents("tr").toggleClass("expanded");
    };

    var agendaItemTable = $("#agenda_items"),
      agendaItemStore = $("tbody", agendaItemTable).clone(),
      updateNumbers = function(numbers) {
        $("tr", agendaItemTable).each(function(idx, row) {
          $(".number", row).html(numbers[$(row).data().uid]);
        });
      },
      onOrderSuccess = function(data) {
        messageFactory.shout(data.messages);
        updateNumbers(data.numbers);
        agendaItemStore = $("tbody", agendaItemTable).clone();
      },
      onOrderFail = function() {
        messageFactory.shout();
        agendaItemTable.html(agendaItemStore.clone());
        $("tbody", agendaItemTable).sortable(sortableSettings);
      },
      onUpdate = function() {
        var payload = { sortOrder: [] };

        $("tr", agendaItemTable).each(function(index, tableRow) {
          payload.sortOrder.push($(tableRow).data().uid);
        });

        $.ajax({
          method: "POST",
          dataType: "json",
          contentType: "application/json",
          url: viewlet.data("update-agenda-item-order-url"),
          data: payload,
          success: onOrderSuccess,
          error: onOrderFail
        });

      },
      sortableSettings = {
        handle: ".sortable_handle",
        forcePlaceholderSize: true,
        opacity: 0.8,
        placeholder: "placeholder",
        items: "tr",
        tolerance: "intersects",
        update: onUpdate
      };

    $("tbody", agendaItemTable).sortable(sortableSettings);

    $(".expandable .toggle-attachements", agendaItemTable).click(toggleAttachements);

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
