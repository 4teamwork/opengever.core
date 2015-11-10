(function(global, $, HBS) {

  "use strict";

  function Controller(template, outlet, options) {

    options = $.extend({ message: true }, options);

    this.outlet = outlet;
    this.template = function() {};
    this.messageFactory = new global.MessageFactory();
    var self = this;

    var messageFunc = function(data) {
      if(data && options.message) {
        self.messageFactory.shout(data.messages);
      }
    };

    this.compile = function() {
      if(template) {
        this.template = HBS.compile(template);
      }
    };

    this.fetch = function() {};

    this.render = function() {};

    this.onRender = function() {};

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
      var target = action.substring(action.indexOf("#") + 1).replace("!", "").replace("$", "");
      var method = action.substring(0, action.indexOf("#"));
      var update = Boolean(action.indexOf("!") > -1);
      var prevent = Boolean(action.indexOf("$") === -1);
      $(document).on(method, target, function(event) { self.trackEvent(event, callback, update, prevent); } );
    };

    this.registerActions = function() { $.each(this.events, this.registerAction); };

    this.init = function() {
      this.compile();
      this.update();
      this.registerActions();
    };

  }

  function AgendaItemController(options) {

    var self = this;
    var viewlet = $("#opengever_meeting_meeting");

    var dialog = $( "#confirm_unschedule" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    var sortableSettings = {
      handle: ".sortable-handle",
      forcePlaceholderSize: true,
      placeholder: "placeholder",
      items: "tr",
      tolerance: "intersects",
      update: self.updateSortOrder
    };

    Controller.call(this, $("#agendaitemsTemplate").html(), $("#agenda_items tbody"), options);

    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ agendaitems: data.items,
                                                                    editable: viewlet.data().editable })); };

    this.openModal = function(e) {
      this.currentItem = $(e.target);
      dialog.load();
    };

    this.unschedule = function() {
      this.closeModal();
      return $.post(this.currentItem.attr("href"));
    };

    this.closeModal = function() { dialog.close(); };

    this.updateSortOrder = function() {
      var numbers = $.map($("tr", this.outlet), function(row) { return $(row).data().uid; });
      return $.post(viewlet.data().updateAgendaItemOrderUrl,
                    { sortOrder: JSON.stringify(numbers) }).fail(function() {
                      self.refresh();
                    });
    };

    var agendaItemTitleValidator = function(data) { return data.proceed; };

    this.showEditbox = function(e) {
      var row = $(e.target).parents("tr");
      row.removeClass("expanded");
      var source;
      if($(".title > span > a", row).length) {
        source = $(".title > span > a", row);
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
      "click#.delete-agenda-item": this.openModal,
      "click#.edit-agenda-item": this.showEditbox,
      "sortupdate##agenda_items tbody!$": this.updateSortOrder,
      "click#.toggle-attachements": this.toggleAttachements,
      "click##confirm_unschedule .confirm!$": this.unschedule,
      "click##confirm_unschedule .decline!": this.closeModal
    };

    this.init();

  }

  function ProposalController(options) {

    var viewlet = $("#opengever_meeting_meeting");
    Controller.call(this, $("#proposalsTemplate").html(), $("#unscheduled_porposals"), options);
    var self = this;
    var title = $("#title");

    this.fetch = function() { return $.get(viewlet.data().listUnscheduledProposalsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ proposals: data.items })); };

    this.schedule = function(e) { return $.post($(e.target).attr("href")); };

    this.addParagraph = function() {
      return $.post($(".schedule-paragraph").data().url, { title: title.val() }).done(function() {
        title.val("");
        self.updateConnected();
      });
    };

    this.addText = function() {
      return $.post($(".schedule-text").first().data().url, { title: title.val() }).done(function() {
        title.val("");
        self.updateConnected();
      });
    };

    this.trackEnter = function(e) {
      if(e.which === $.ui.keyCode.ENTER) {
        this.addText();
      }
    };

    this.events = {
      "click#.schedule-proposal!": this.schedule,
      "click#.schedule-paragraph": this.addParagraph,
      "click#.schedule-text": this.addText,
      "keyup##title": this.trackEnter
    };

    this.init();

  }

  function CollapsibleController() {

    Controller.call(this);

    this.toggle = function(e) { $(e.target).parents(".collapsible").toggleClass("open"); };

    this.events = {
      "click#.collapsible-header > button": this.toggle
    };

    this.init();

  }

  $(function() {
    if($("#opengever_meeting_meeting").length) {

      var agendaItemController = new AgendaItemController();
      var proposalsController = new ProposalController();
      var collapsibleController = new CollapsibleController();

      proposalsController.connectedTo = [agendaItemController];
      agendaItemController.connectedTo = [proposalsController];
    }
  });

}(window, jQuery, window.Handlebars));
