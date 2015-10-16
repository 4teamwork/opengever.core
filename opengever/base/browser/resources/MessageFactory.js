(function(global, $){

  "use strict";

  var MessageFactory = function(viewlet) {

    var messageTemplate = "<dl style='display:none'; class='portalMessage {{:messageClass}}'><dt>{{:messageTitle}}</dt><dd>{{:message}}</dd></dl>";
    var defaultMessage = {
      messageClass: "error",
      messageTitle: "Fehler",
      message: viewlet.data("msg_unexpected_error")
    };

    this.clearMessages = function() {
      var currentMessages = $(".portalMessage:visible");
      currentMessages.delay(500).fadeOut("fast", function() {
        $(this).remove();
      });
    };

    this.insertMessage = function(messageData) {
      var lastPloneMessage = $(".portalMessage").last();
      var message = messageTemplate;
      message = message.replace("{{:messageClass}}", messageData.messageClass);
      message = message.replace("{{:messageTitle}}", messageData.messageTitle);
      message = message.replace("{{:message}}", messageData.message);
      $(message).insertAfter(lastPloneMessage).fadeIn("fast");
    };

    this.shout = function(messages) {
      this.clearMessages();
      var self = this;
      if (!messages) {
        this.insertMessage(defaultMessage);
      } else {
        $.each(messages, function(index, message) {
          self.insertMessage(message);
        });
      }
    };

  };

  global.MessageFactory = MessageFactory;

}(window, jQuery));
