(function(global, $){

  "use strict";

  var instance = null;

  var MessageFactory = function() {

    var settings = {
      autoHideDelay: 5000,
      arrowShow: false,
      showAnimation: "fadeIn",
      hideAnimation: "fadeOut",
      style: "gever"
    };

    var root = $(document);

    var messageTemplate = " \
      <div> \
          <span class='title' data-notify-text='title'></span> \
          <span class='message' data-notify-text='message'></span> \
      </div> \
    ";

    $.notify.addStyle(settings.style, {
      html: messageTemplate
    });

    this.clearMessages = function() { $(".portalMessage:visible").remove(); };

    this.notify = function(messageData) {
      messageData = $.extend({
        messageTitle: $("#default-error-message dt").text(),
        message: $("#default-error-message dd").text()
      }, messageData || {});

      settings.className = messageData.messageClass;

      $.notify({
        title: messageData.messageTitle,
        message: messageData.message
      }, settings);

      root.trigger("notify");

    };

    this.shout = function(messages) {
      var self = this;
      if (!messages) {
        this.notify();
      } else {
        $.each(messages, function(index, message) {
          self.notify(message);
        });
      }
    };

  };

  MessageFactory.getInstance = function() {
    if(instance === null) {
      instance = new MessageFactory();
    }
    return instance;
  };

  global.MessageFactory = MessageFactory;

}(window, jQuery));
