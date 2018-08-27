/*

  This is the base class for all controllers in the opengever.meeting


  Initializing
  ============

  You can simply create your own controller by inheriting from the base Controller:

  function MyController() {
    global.Controller.call(this); // Inherit the base controller
    this.init(); // Call the init function of the base Controller
  }

  You have to call the `init` function first before you can use the controller.
  The init function will compile the Handlebars template, fetch the initial data
  and register the events.

  The controller accepts the following options:

  - template:            Specifiy the handlebars template as an HTML string
  - outlet:              Specify the target where the controller has to render the template
                         by passing a DOM element.
                         The whole container will be replaced by the rendered HTML.
  - options.showMessage: Set this option to false to turn off all messages.
  - options.context:     This option sets the context where all events are going to be attached.

  function MyController(options) {
    global.Controller.call(this, $("#template").html(), $("#outlet"), options);
    this.init();
  }

  To initialize the controller you have to instantiate the controller

  var myController = new MyController();


  Fetching
  ========

  You have to tell your controller how to fetch data by overriding
  the `fetch` function.
  Because the `fetch` function in the base class does nothing at this point.
  To make the `fetch` function work simply return a jQuery Deferred object (https://api.jquery.com/category/deferred-object/).

  Here is an example for fetching using jQuery's `get` function:

  function MyController(options) {
    global.Controller.call(this, $("#template").html(), $("#outlet"), options);

    this.fetch = function() { return $.get("http://someurl.com") };

    this.init();
  }


  Rendering
  =========

  You have to tell your controller how to render the received data
  by overriding the `render` function.
  Because the `render` function in the base class does nothing at this point.
  To make the `render` function work you have to simply return some HTML.
  The rendered HTML will automatically replace the outlet section.
  You will get the data in the render function as a parameter.
  The template is bound to the current context as a handlebars function.

  function MyController(options) {
    global.Controller.call(this, $("#template").html(), $("#outlet"), options);

    this.fetch = function() { return $.get("http://someurl.com") };

    this.render = function(data) { return this.template({ data: data }); }

    this.init();
  }


  Event Registration
  ==================

  The controller is able to carry a list of events.
  To pass the action throug the controller chain simply return a jQuery Deferred object.
  Returning a plain object will always succeed.

  Each event has the following parts.

  - method:          This is the event type of your event e.q. `click`, `mouseover` or some custom events
                     triggered by yourself.
  - target:          Pass a CSS selector where the controller should catch the event.
  - callback:        Define a callback function which will be called when the event gets fired.
                     You will get the target DOM element and the event as callback parameters.
  - options.update:  Set this to true to automatically update the handlebars template
                     after a successful call of your action.
  - options.prevent: Set this to false so the controller would not prevent the default
                     Browser behaviour.

  - options.loading: Set this to true so the clicked target would turn into a loading element and gets back to
                     normal when the action and probably the update request has been terminated.

  function MyController(options) {
    global.Controller.call(this, $("#template").html(), $("#outlet"), options);

    this.fetch = function() { return $.get("http://someurl.com") };

    this.render = function(data) { return this.template({ data: data }); }

    this.init();

    this.postSomething = function(target, event) {
      return $.post("http://someurl.com/post", { data: "something" });
    }

    this.events = [
      {
        method: "click",
        target: "#action",
        callback: this.doSomething
        options: {
          update: true
        }
      }
    ]
  }

  Because the update option in the event is set to true the controller will automatically
  fetch the new generated record of the `postSomething` function as long as the request succeeded.


  Messages
  ========

  Each response can contain a list of messages as JSON.

  The message object looks as follows:

  messages: [
    {
      messageClass: 'info',
      messageTitle: 'Just some Information',
      message: 'This message is very important'
    }
  ]

  The message class sets the severity of the message. It can be `info`, `warn` or `error`.


  Validator
  =========

  The controller is able to pass each response throug a validator by using the internal `request` function.
  This function wraps jQuery `ajax` function to pipe the validator (http://api.jquery.com/jquery.ajax).
  The default validator only accepts the response when `proceed` is set to true.
  But you can simply override the default validator.
  As callback parameter you will get the returned data from the request.
  The validator will only pass the whole request chain if the returned value is truthy.
  Otherwise the request will reject.
  So you can manipulate the response before reaching the event callback.

  function MyController(options) {
    global.Controller.call(this, $("#template").html(), $("#outlet"), options);

    this.fetch = function() { return $.get("http://someurl.com") };

    this.render = function(data) { return this.template({ data: data }); }

    this.init();

    var validator = function(data) { return data.isSave; };

    this.doSomethingValidated = function(target, event) {
      return this.request("http://someurl.com", {
        method: "POST",
        data: { data: "something" },
        validator: validator
      }).done(function() { console.log("Everything went good."); })
      .fail(function() { console.log("Something went wrong"); });
    }

    this.events = [
      {
        method: "click",
        target: "#action",
        callback: this.doSomething
        options: {
          update: true
        }
      }
    ]
  }

  Connect Controllers
  ===================

  You can set dependencies between controllers by passing controller objects to the `connected to` option.
  The connected controllers will automatically update.
  Circular dependencies are also possible.

  function MyController(options) {
    global.Controller.call(this);
    this.init();
  }

  function OtherController() {
    global.Controller.call(this);
    this.init();
  }

  function AgainController() {
    global.Controller.call(this);
    this.init();
  }

  var myController = new MyController();
  var otherController = new OtherController();
  var againController = new AgainController();

  myController.connectedTo = [otherController, againController];
  otherController.connectedTo = [myController];
  againController.connectedTo = [myController];

 */

(function(global, $, HBS, MessageFactory) {

  "use strict";

  function Controller(template, outlet, options) {

    options = $.extend({ showMessage: true, context: $(document) }, options);

    template = template || "";
    this.outlet = outlet || $();
    this.template = $.noop;
    this.messageFactory = MessageFactory.getInstance();
    var self = this;

    var messageFunc = function(data) {
      if(data && data.messages && !data.redirectUrl && options.showMessage) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.compile = function() { this.template = HBS.compile(template); };

    this.fetch = $.noop;

    this.render = $.noop;

    this.onRender = $.noop;

    this.validator = function(data) { return data && data.proceed !== false; };

    this.refresh = function() { this.outlet.html(this.render(this.cache)); };

    this.update = function() {
      return $.when(self.fetch()).fail(messageFunc).done(function(data) {
        self.cache = data;
        self.outlet.html(self.render(data));
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

    this.trackEvent = function(event, callback, options, payload) {
      var target = $(event.currentTarget);
      var request = $.Deferred();
      var actionRequest = $.when(callback.call(self, target, event, payload));

      if(options.prevent) { event.preventDefault(); }

      if(options.loading) { target.addClass("loading"); }

      actionRequest.done(function(data) {
        if(options.update) {
          $.when(self.update(), self.updateConnected()).done(function() {
            request.resolve(data);
          }).fail(function() {
            request.reject();
          });
        } else {
          request.resolve(data);
        }
      }).fail(function(response) { request.reject(response.responseJSON); });

      request.done(function() {
        if(options.loading) { target.removeClass("loading"); }
      }).always(messageFunc);
    };

    this.registerAction = function(_, action) {
      action.options = $.extend({
        update: false,
        prevent: true
      }, action.options);

      options.context.on(action.method, action.target, function(event, payload) {
        self.trackEvent(event, action.callback, action.options, payload);
      });
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
        target: ".collapsible-header > button, .collapsible-header > span",
        callback: this.toggle,
        loading: false
      }
    ];

    this.init();

  }

  global.CollapsibleController = CollapsibleController;

  $(function() { new CollapsibleController(); });

}(window, jQuery, window.Handlebars, window.MessageFactory));
