(function(global, $) {

  "use strict";

  var listMessages = function(messages) {

    var lastPloneMessage = $(".portalMessage").last();
    var messageTemplate = "<dl style='display:none'; class='portalMessage {{:messageClass}}'><dt>{{:messageTitle}}</dt><dd>{{:message}}</dd></dl>";
    var defaultMessage = {
      messageClass: "error",
      messageTitle: "Fehler",
      message: global.msg_unexpected_error
    };
    var currentMessages = $(".portalMessage:visible");

    var clearMessages = function() {
      currentMessages.delay(500).fadeOut("fast", function() {
        $(this).remove();
      });
    };

    var insertMessage = function(messageData) {
      var message = messageTemplate;
      message = message.replace("{{:messageClass}}", messageData.messageClass);
      message = message.replace("{{:messageTitle}}", messageData.messageTitle);
      message = message.replace("{{:message}}", messageData.message);
      $(message).insertAfter(lastPloneMessage).fadeIn("fast");
    };

    if (!messages) {
      insertMessage(defaultMessage);
    } else {
      $.each(messages, function(index, message) {
        insertMessage(message);
      });
    }

    clearMessages();

  };

  $(function() {

    $("#opengever_meeting_protocol textarea").autosize();

    stickyHeading("#opengever_meeting_protocol .protocol_title");

    var agendaItemTable = $("#agenda_items"),
      agendaItemStore = $("tbody", agendaItemTable).clone(),
      updateNumbers = function(numbers) {
        $("tr", agendaItemTable).each(function(idx, row) {
          $(".number", row).html(numbers[row.dataset.uid]);
        });
      },
      onOrderSuccess = function(data) {
        listMessages(data.messages);
        updateNumbers(data.numbers);
        agendaItemStore = $("tbody", agendaItemTable).clone();
      },
      onOrderFail = function() {
        listMessages();
        agendaItemTable.html(agendaItemStore.clone());
        $("tbody", agendaItemTable).sortable(sortableSettings);
      },
      onUpdate = function() {
        var updatePayload = {
          sortOrder: []
        };

        $("tr", agendaItemTable).each(function(index, tableRow) {
          updatePayload.sortOrder.push(tableRow.dataset.uid);
        });

        $.ajax({
          type: "POST",
          dataType: "json",
          contentType: "application/json",
          url: global.js_update_order_url, // this variable is set by the template
          data: JSON.stringify(updatePayload),
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

  });

}(window, jQuery));
