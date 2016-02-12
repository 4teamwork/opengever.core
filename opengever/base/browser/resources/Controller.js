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
      if(data && !data.redirectUrl && options.message) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.compile = function() { this.template = HBS.compile(template); };

    this.fetch = $.noop;

    this.render = $.noop;

    this.onRender = $.noop;

    this.validator = function(data) { return data && data.proceed !== false; };

    this.refresh = function() { this.render(this.cache); };

    this.update = function() {
      $.when(self.fetch()).fail(messageFunc).done(function(data) {
        self.cache = data;
        self.render(data);
        self.onRender.call(self);
      });
    };

    this.connectedTo = [];

    this.events = [];

    this.updateConnected = function() {
      $.each(this.connectedTo, function(controllerIdx, controller) {
        controller.update();
      });
    };

    this.request = function(url, settings) {
      var validator = settings.validator || this.validator;
      var valid = new $.Deferred();
      return $.ajax(url, settings).pipe(function(data) {
        if(validator(data)) {
          return valid.resolve(data);
        } else {
          return valid.reject(data);
        }
      });
    };

    this.trackEvent = function(event, callback, options) {
      if(options.prevent) {
        event.preventDefault();
      }

      var eventCallback = $.when(callback.call(self, $(event.currentTarget), event));

      eventCallback.done(function() {
        if(options.update) {
          self.update();
          self.updateConnected();
        }
      }).always(messageFunc);
    };

    this.registerAction = function(_, action) {
      action.options = $.extend({
        update: false,
        prevent: true
      }, action.options);

      console.log(action);
      options.context.on(action.method, action.target, function(event) {
        self.trackEvent(event, action.callback, action.options);
      } );
    };

    this.unregisterAction = function(action) {
      options.context.off(action.method);
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

    this.events = [
      {
        method: "click",
        target: ".collapsible-header > button",
        callback: this.toggle
      }
    ];

    this.init();

  }

  global.CollapsibleController = CollapsibleController;

  $(function() {
    var collapsibleController = new global.CollapsibleController();
  });

}(window, jQuery, window.Handlebars));
