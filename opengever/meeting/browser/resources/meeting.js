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
      onUpdate = function() {
        var updatePaylod = {
          agenda: []
        };

        $("tr", agendaItemTable).each(function(index, tableRow) {
          updatePaylod.agenda.push(tableRow.dataset.uid);
        });

        $.ajax({
          url: "@@update_agenda_item_order",
          dataType: "json",
          data: JSON.stringify(updatePaylod),
          success: function(data) {
            listMessages(data.messages);
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
