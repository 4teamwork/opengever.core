(function(global, $) {

  "use strict";

  var Editbox = function(options) {

    options = $.extend({
      trigger: ".editbox_trigger",
      editbox: ".editbox",
      source: ".source",
      onChange: function(){},
      responseValidator: function(){},
      onUpdateFail: function(){}
    }, options);

    this.editbox = $(options.editbox);
    this.trigger = $(options.trigger);
    this.saveTrigger = $(".edit-save", this.editbox);
    this.cancelTrigger = $(".edit-cancel", this.editbox);
    this.input = $("input[type='text']", this.editbox);
    this.source = $(options.source);
    var self = this;

    this.show = function() {
      self.source.hide();
      self.input.val(self.source.text().trim());
      self.editbox.show();
      self.input.focus();
    };

    this.hide = function() {
      this.editbox.hide();
      this.source.show();
    };

    this.cancel = function() { self.hide(); };

    this.save = function(data) {
      if(options.responseValidator(data)) {
        self.source.text(self.input.val());
        self.hide();
      } else {
        self.cancel();
        options.onUpdateFail.call(self, data);
      }
    };

    this.onChange = function() {
      $.when(options.onChange.call(self, self.input.val()))
            .done(self.save)
            .fail(self.cancel);
    };

    this.trigger.on("click", this.show);

    this.cancelTrigger.on("click", this.cancel);

    this.saveTrigger.on("click", this.onChange);

    this.input.on("keyup", function(event) {
      switch (event.which) {
        case $.ui.keyCode.ENTER:
          self.onChange();
          break;
        case $.ui.keyCode.ESCAPE:
          self.cancel();
          break;
      }
    });

  };

  window.Editbox = Editbox;

  return Editbox;

}(window, jQuery));
