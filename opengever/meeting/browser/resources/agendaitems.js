(function(global, $, HBS) {

  "use strict";

  function Controller(viewlet, template, outlet) {

    this.viewlet = viewlet;
    this.outlet = outlet;
    this.template = HBS.compile(template);
    this.messageFactory = new global.MessageFactory(viewlet);
    var self = this;

    var messageFunc = function(data) {
      if(data && data.messages) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.fetch = function() {};

    this.render = function() {};

    this.update = function() { self.fetch().always(messageFunc).done(self.render); };

    this.connectedTo = [];

    this.events = {};

    this.registerEvents = function() {
      $.each(this.events, function(idx, callback) {
        var method = idx.split("#")[0];
        var target = idx.split("#")[1];
        $(document).on(method, target, function(e) {
          e.preventDefault();
          var callbackPromise = callback.call(self, e);
          if(callbackPromise && callbackPromise.done) {
            callbackPromise.always(messageFunc).done(self.update);
            $.each(self.connectedTo, function(controllerIdx, controller) {
              controller.update();
            });
          }
        });
      });
    };

    this.init = function() {
      this.registerEvents();
      self.update();
    };

  }

  window.Controller = Controller;

  function AgendaItemController() {

    var self = this;
    var viewlet = $("#opengever_meeting_meeting");
    Controller.call(this, viewlet, $("#agendaitemsTemplate").html(), $("#agenda_items tbody"));

    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ agendaitems: data.items })); };

    this.delete = function(e) { return $.post($(e.target).attr("href")); };

    this.agendaItemTitleValidator = function(data) { return data.proceed; };

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
        responseValidator: self.agendaItemTitleValidator
      });

      editbox.show();
    };

    this.edit = function(title) {
      return $.post(this.trigger.attr("href"), { title: title }).done(this.onUpdateSuccess).fail(this.onUpdateFail);
    };

    this.onUpdateSuccess = function(data) { this.messageFactory.shout(data.messages); };

    this.onUpdateFail = function(data) { this.messageFactory.shout(JSON.parse(data.responseText).messages); };

    this.events = {
      "click#.delete-agenda-item": this.delete,
      "click#.edit-agenda-item": this.showEditbox
    };

  }

  function ProposalController() {

    var viewlet = $("#opengever_meeting_meeting");
    Controller.call(this, viewlet, $("#proposalsTemplate").html(), $("#unscheduled_porposals"));
    var self = this;

    this.fetch = function() { return $.get(viewlet.data().listUnscheduledProposalsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ proposals: data.items })); };

    this.schedule = function(e) { return $.post($(e.target).attr("href")); };

    this.add = function(e) {
      var title = $("#title");
      return $.post($(e.target).data().url, { title: title.val() }).done(title.val(""));
    };

    this.events = {
      "click#.schedule-proposal": this.schedule,
      "click#.schedule-paragraph": this.add,
      "click#.schedule-text": this.add
    };

  }

  //   var sortableSettings = {
  //     handle: ".sortable-handle",
  //     forcePlaceholderSize: true,
  //     opacity: .8,
  //     placeholder: "placeholder",
  //     items: "tr",
  //     tolerance: "intersects",
  //     update: function() { self.extractNumbers(); }
  //   };

  //   this.updateNumbers = function(numbers) {
  //     $.post(options.updateUrl, { sortOrder: JSON.stringify(numbers) }).done(function(data) {
  //       self.fetch();
  //       messageFactory.shout(data.messages);
  //     }).fail(function(data) {
  //       messageFactory.shout(data.messages);
  //       self.render();
  //     });

  //   };

  //   this.extractNumbers = function() {
  //     var numbers = $.map($("tr", options.outlet), function(row) {
  //       return $(row).data().uid;
  //     });
  //     self.updateNumbers(numbers);
  //   };


  $(function() {
    var agendaItemController = new AgendaItemController();
    agendaItemController.init();

    var proposalsController = new ProposalController();
    proposalsController.init();

    proposalsController.connectedTo = [agendaItemController];
    agendaItemController.connectedTo = [proposalsController];
  });

}(window, jQuery, window.Handlebars));
