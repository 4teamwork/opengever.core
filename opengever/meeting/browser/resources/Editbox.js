(function(global, $) {

  "use strict";

  var EditboxController = function(options) {

    global.Controller.call(this, "", null, { context: options.editbox });

    var self = this;

    var input = $('input[type="text"]', options.editbox);

    var value = function() { return input.val().trim(); };

    var source = function() { return options.source.text().trim(); };

    this.show = function() {
      options.source.hide();
      input.val(source());
      options.editbox.show();
      input.focus();
    };

    this.hide = function() {
      options.editbox.hide();
      options.source.show();
    };

    this.cancel = $.proxy(function() {
      this.hide();
      this.destroy();
    }, this);

    this.save = $.proxy(function() {
      options.source.text(value());
      this.hide();
      this.destroy();
    }, this);

    this.updateValue = function() {
      return this.request(options.trigger.attr("href"),
        {
          method: "POST",
          data: { title: value() }
        }
      ).done(this.save)
       .fail(this.cancel);
    };

    this.trackKey = function(target, event) {
      var result;
      switch (event.which) {
        case $.ui.keyCode.ENTER:
          result = self.updateValue();
          break;
        case $.ui.keyCode.ESCAPE:
          result = self.cancel();
          break;
      }
      return result;
    };

    this.events = {
      "click#.edit-cancel": this.cancel,
      "click#.edit-save": this.updateValue,
      "keyup#input": this.trackKey
    };

    this.init();

    this.show();

  };

  window.EditboxController = EditboxController;

}(window, jQuery));
