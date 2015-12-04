(function(global, $, HBS) {

  "use strict";

  function Controller(template, outlet, options) {

    options = $.extend({ message: true, context: $(document) }, options);

    template = template || "";
    this.outlet = outlet;
    this.template = function() {};
    this.messageFactory = global.MessageFactory.getInstance();
    var self = this;

    var messageFunc = function(data) {
      if(data && options.message) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.compile = function() { this.template = HBS.compile(template); };

    this.fetch = $.noop;

    this.render = $.noop;

    this.onRender = $.noop;

    this.validator = function(data) { return data && data.proceed !== false; };

    this.refresh = function() { this.render(this.chache); };

    this.update = function() {
      $.when(self.fetch()).fail(messageFunc).done(function(data) {
        self.chache = data;
        self.render(data);
        self.onRender.call(self);
      });
    };

    this.connectedTo = [];

    this.events = {};

    this.proceed = $.noop;

    this.remain = $.noop;

    this.updateConnected = function() {
      $.each(this.connectedTo, function(controllerIdx, controller) {
        controller.update();
      });
    };

    this.cleanHooks = function() {
      this.proceed = $.noop;
      this.remain = $.noop;
    };

    this.trackEvent = function(event, callback, update, prevent) {
      if(prevent) {
        event.preventDefault();
      }

      var eventCallback = $.when(callback.call(self, $(event.currentTarget), event));

      eventCallback.pipe(function(data) {
        var validator = new $.Deferred();
        if(self.validator(data)) {
          validator.resolve(data);
        } else {
          validator.reject(data);
        }
        return validator.promise();
      }).done(function() {
          if(update) {
            self.update();
            self.updateConnected();
          }
          self.proceed();
        })
        .fail(function() { self.remain(); })
        .always(function(data) {
          self.cleanHooks();
          messageFunc(data);
        });
    };

    this.registerAction = function(action, callback) {
      var target = action.substring(action.indexOf("#") + 1).replace("!", "").replace("$", "");
      var method = action.substring(0, action.indexOf("#"));
      var update = Boolean(action.indexOf("!") > -1);
      var prevent = Boolean(action.indexOf("$") === -1);
      options.context.on(method, target, function(event) { self.trackEvent(event, callback, update, prevent); } );
    };

    this.unregisterAction = function(action) {
      var method = action.substring(0, action.indexOf("#"));
      options.context.off(method);
    };

    this.registerActions = function() { $.each(this.events, this.registerAction); };

    this.unregisterActions = function() { $.each(this.events, this.unregisterAction); };

    this.init = function() {
      this.compile();
      this.update();
      this.registerActions();
    };

    this.destroy = function() { this.unregisterActions(); };

  }

  global.Controller = Controller;

  function CollapsibleController() {

    Controller.call(this);

    this.toggle = function(target) { target.parents(".collapsible").toggleClass("open"); };

    this.events = {
      "click#.collapsible-header > button": this.toggle
    };

    this.init();

  }

  global.CollapsibleController = CollapsibleController;

  $(function() {
    var collapsibleController = new global.CollapsibleController();
  });

}(window, jQuery, window.Handlebars));
