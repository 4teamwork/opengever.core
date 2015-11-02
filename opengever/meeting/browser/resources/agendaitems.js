(function(global, $, HBS) {

  "use strict";

  function Controller(viewlet, template, outlet, options) {

    options = $.extend({ message: true }, options);

    this.viewlet = viewlet;
    this.outlet = outlet;
    this.template = HBS.compile(template);
    this.messageFactory = new global.MessageFactory(viewlet);
    var self = this;

    var messageFunc = function(data) {
      if(data && options.message) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.fetch = function() {};

    this.render = function() {};

    this.onRender = function() {};

    this.update = function() {
      self.fetch().fail(messageFunc).done(function(data) {
        self.render(data);
        self.onRender.call(self);
      });
    };

    this.connectedTo = [];

    this.events = {};

    this.updateConnected = function() {
      $.each(this.connectedTo, function(controllerIdx, controller) {
        controller.update();
      });
    };

    this.trackEvent = function(event, callback, update, prevent) {
      if(prevent) {
        event.preventDefault();
      }
      $.when(callback.call(self, event)).always(messageFunc).done(function() {
        if(update) {
          self.update();
          self.updateConnected();
        }
      });
    };

    this.registerAction = function(action, callback) {
      var target = action.substring(action.indexOf("#") + 1).replace("!", "");
      var method = action.substring(0, action.indexOf("#"));
      var update = Boolean(action.indexOf("!") > -1);
      var prevent = Boolean(action.indexOf("$") === -1);
      $(document).on(method, target, function(event) { self.trackEvent(event, callback, update, prevent); } );
    };

    this.registerActions = function() { $.each(this.events, this.registerAction); };

    this.init = function() {
      this.registerActions();
      this.update();
    };

  }

  function AgendaItemController(options) {

    var self = this;
    var viewlet = $("#opengever_meeting_meeting");

    var sortableSettings = {
      handle: ".sortable-handle",
      forcePlaceholderSize: true,
      placeholder: "placeholder",
      items: "tr",
      tolerance: "intersects",
      update: self.updateSortOrder
    };

    Controller.call(this, viewlet, $("#agendaitemsTemplate").html(), $("#agenda_items tbody"), options);

    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ agendaitems: data.items })); };

    this.unschedule = function(e) { return $.post($(e.target).attr("href")); };


    this.updateSortOrder = function() {
      var numbers = $.map($("tr", this.outlet), function(row) { return $(row).data().uid; });
      return $.post(viewlet.data().updateAgendaItemOrderUrl, { sortOrder: JSON.stringify(numbers) });
    };

    var agendaItemTitleValidator = function(data) { return data.proceed; };

    this.showEditbox = function(e) {
      var row = $(e.target).parents("tr");
      var source;
      if($(".title > a", row).length) {
        source = $(".title > a", row);
      } else {
        source = $(".title > span", row);
      }
      var editbox = new global.Editbox({
        editbox: $(".edit-box", row),
        source: source,
        trigger: $(e.target),
        onChange: self.edit,
        onUpdateFail: self.onUpdateFail,
        responseValidator: agendaItemTitleValidator
      });

      editbox.show();
    };

    this.onRender = function() { this.outlet.sortable(sortableSettings); };

    this.edit = function(title) { return $.post(this.trigger.attr("href"), { title: title }); };

    this.onUpdateFail = function(data) { self.messageFactory.shout(data.messages); };

    this.toggleAttachements = function(e) { $(e.target).parents("tr").toggleClass("expanded"); };

    this.events = {
      "click#.delete-agenda-item!": this.unschedule,
      "click#.edit-agenda-item": this.showEditbox,
      "sortupdate##agenda_items tbody$!": this.updateSortOrder,
      "click#.toggle-attachements": this.toggleAttachements
    };

    this.init();

  }

  function ProposalController(options) {

    var viewlet = $("#opengever_meeting_meeting");
    Controller.call(this, viewlet, $("#proposalsTemplate").html(), $("#unscheduled_porposals"), options);
    var self = this;

    this.fetch = function() { return $.get(viewlet.data().listUnscheduledProposalsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ proposals: data.items })); };

    this.schedule = function(e) { return $.post($(e.target).attr("href")); };

    this.add = function(e) {
      var title = $("#title");
      return $.post($(e.target).data().url, { title: title.val() }).done(title.val(""));
    };

    this.events = {
      "click#.schedule-proposal!": this.schedule,
      "click#.schedule-paragraph!": this.add,
      "click#.schedule-text!": this.add
    };

    this.init();

  }

  $(function() {
    if($("#opengever_meeting_meeting").length) {
      var agendaItemController = new AgendaItemController();
      var proposalsController = new ProposalController();

      proposalsController.connectedTo = [agendaItemController];
      agendaItemController.connectedTo = [proposalsController];
    }
  });

}(window, jQuery, window.Handlebars));
