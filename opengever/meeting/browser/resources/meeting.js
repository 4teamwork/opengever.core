(function(global, $) {

  "use strict";

  var listMessages = function(messages) {

    var lastPloneMessage = $(".portalMessage").last();
    var messageTemplate = "<dl style='display:none'; class='portalMessage {{:messageClass}}'><dt>{{:messageTitle}}</dt><dd>{{:message}}</dd></dl>";
    var defaultMessage = {
      messageClass: "error",
      messageTitle: "Fehler",
      message: "Es ist ein unerwarteter Fehler aufgetreten."
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
    var agendaItemTable = $("#agenda_items"),
    updateNumbers = function(numbers) {
      $("tr", agendaItemTable).each(function(idx, row) {
        $(".number", row).html(numbers[row.dataset.uid]);
      });
    },
      onUpdate = function() {
        var updatePaylod = {
          sortOrder: []
        };

        $("tr", agendaItemTable).each(function(index, tableRow) {
          updatePaylod.sortOrder.push(tableRow.dataset.uid);
        });

        $.ajax({
          type: "POST",
          dataType: "json",
          contentType: "application/json",
          url: js_update_order_url, // this variable is set by the template
          data: JSON.stringify(updatePaylod),
          success: function(data) {
            listMessages(data.messages);
            updateNumbers(data.numbers);
          },
          error: function() {
            listMessages();
          }
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
