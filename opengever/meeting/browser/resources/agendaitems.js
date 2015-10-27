(function(global, $, HBS) {

  "use strict";


  function Agendaitems(options, messageFactory) {

    options = $.extend({

    }, options);

    this.template = HBS.compile(options.template);

    this.store = {};

    var self = this;

    var sortableSettings = {
      handle: ".sortable-handle",
      forcePlaceholderSize: true,
      opacity: .8,
      placeholder: "placeholder",
      items: "tr",
      tolerance: "intersects",
      update: function() { self.extractNumbers(); }
    };

    this.toggleAttachement = function(event) {
      var attachement = $(".attachements", $(event.target).parents("tr"));
      attachement.toggleClass("open");
    };

    this.render = function(data) {
      options.outlet.html(self.template({ agendaitems: data }));
    };

    this.fetch = function() {
      $.get(options.readUrl).done(function(data) {
        self.render(data.items);
      }).fail(function(data) {
        messageFactory.shout(data.messages);
      });
    };

    this.updateNumbers = function(numbers) {
      $.post(options.updateUrl, { sortOrder: JSON.stringify(numbers) }).done(function(data) {
        self.fetch();
        messageFactory.shout(data.messages);
      }).fail(function(data) {
        messageFactory.shout(data.messages);
        self.render();
      });

    };

    this.extractNumbers = function() {
      var numbers = $.map($("tr", options.outlet), function(row) {
        return $(row).data().uid;
      });
      self.updateNumbers(numbers);
    };

    this.delete = function(event) {
      event.preventDefault();
      var url = $(event.target).attr("href");
      $.post(url).done(function(data) {
        messageFactory.shout(data.messages);
        self.fetch();
      }).fail(function(data) {
        messageFactory.shout(data.messages);
      });
    };

    this.update = function(event) {
      event.preventDefault();
      var url = $(event.target).attr("href");
    };

    this.addProposal = function(event) {
      event.preventDefault();
      var url = $(event.target).attr("href");
      $.post(url).done(function(data) {
        messageFactory.shout(data.messages);
        self.fetch();
      }).fail(function(data) {
        messageFactory.shout(data.messages);
      });
    };

    this.fetch();

    options.outlet.sortable(sortableSettings);

    options.outlet.on("click", ".toggle-attachements-btn", this.toggleAttachement);

    options.outlet.on("click", ".delete-agenda-item", this.delete);

    $(".add-proposal").on("click", this.addProposal);

  }

  $(function() {
    var viewlet = $("#opengever_meeting_meeting");

    var messageFactory = new global.MessageFactory(viewlet);

    var agendaitems = new Agendaitems({
      outlet: $("#agenda_items tbody"),
      template: $("#agendaitemsTemplate").html(),
      readUrl: viewlet.data().listAgendaItemsUrl,
      updateUrl: viewlet.data().updateAgendaItemOrderUrl
    }, messageFactory);

  });

}(window, jQuery, window.Handlebars));
