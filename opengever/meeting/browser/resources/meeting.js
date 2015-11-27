(function(global, $) {

  "use strict";

  function MeetingController() {

    global.Controller.call(this);

    var self = this;

    var dialog = $( "#confirm_close_meeting" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    this.openModal = function(target) {
      self.currentItem = target;
      dialog.load();
    };

    this.closeMeeting = function() {
      this.closeModal();
      window.location.href = self.currentItem.attr("href");
    };

    this.closeModal = function() { dialog.close(); };

    this.events = {
      "click##pending-closed": this.openModal,
      "click##confirm_close_meeting .confirm!$": this.closeMeeting,
      "click##confirm_close_meeting .decline!": this.closeModal
    };

    this.init();

  }

  function AgendaItemController(options) {

    var self = this;
    var viewlet = $("#opengever_meeting_meeting");

    var dialog = $( "#confirm_unschedule" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    var sortableHelper = function(e, row) {
      var helper = row.clone();
      $.each(row.children(), function(idx, cell) {
        helper.children().eq(idx).width($(cell).width());
      });
      return helper;
    };

    var sortableSettings = {
      handle: ".sortable-handle",
      forcePlaceholderSize: true,
      placeholder: "placeholder",
      items: "tr",
      tolerance: "intersects",
      update: self.updateSortOrder,
      helper: sortableHelper
    };

    global.Controller.call(this, $("#agendaitemsTemplate").html(), $("#agenda_items tbody"), options);

    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) {
      self.outlet.html(self.template({
        agendaitems: data.items,
        editable: viewlet.data().editable,
        agendalist_editable: viewlet.data().agendalist_editable
      }));
    };

    this.openModal = function(target) {
      this.currentItem = target;
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

    this.showEditbox = function(target) {
      var row = target.parents("tr");
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
        trigger: target,
        onChange: self.edit,
        onUpdateFail: self.onUpdateFail,
        responseValidator: agendaItemTitleValidator
      });

      editbox.show();
    };

    this.onRender = function() { this.outlet.sortable(sortableSettings); };

    this.edit = function(title) { return $.post(this.trigger.attr("href"), { title: title }); };

    this.onUpdateFail = function(data) { self.messageFactory.shout(data.messages); };

    this.toggleAttachements = function(target) { target.parents("tr").toggleClass("expanded"); };

    this.decide = function(target) {
      target.addClass('loading');
      return $.post(target.attr("href")).always(function(){
        target.removeClass('loading');
      });
    };

    this.events = {
      "click#.delete-agenda-item": this.openModal,
      "click#.edit-agenda-item": this.showEditbox,
      "click#.decide-agenda-item!": this.decide,
      "sortupdate##agenda_items tbody!$": this.updateSortOrder,
      "click#.toggle-attachements": this.toggleAttachements,
      "click##confirm_unschedule .confirm!$": this.unschedule,
      "click##confirm_unschedule .decline!": this.closeModal
    };

    this.init();

  }

  function ProposalController(options) {

    var viewlet = $("#opengever_meeting_meeting");
    global.Controller.call(this, $("#proposalsTemplate").html(), $("#unscheduled_porposals"), options);
    var self = this;

    this.fetch = function() { return $.get(viewlet.data().listUnscheduledProposalsUrl); };

    this.render = function(data) { self.outlet.html(self.template({ proposals: data.items })); };

    this.schedule = function(target) {
      return $.post(target.attr("href")).done(function() { $("#filter-proposals").val(""); });
    };

    this.addParagraph = function() {
      var input = $("#schedule-paragraph");
      return $.post($(".schedule-paragraph").data().url, { title: input.val() }).done(function() {
        input.val("");
        self.updateConnected();
      });
    };

    this.addText = function() {
      var input = $("#schedule-text");
      return $.post($(".schedule-text").first().data().url, { title: input.val() }).done(function() {
        input.val("");
        self.updateConnected();
      });
    };

    this.trackText = function(target, event) {
      if(event.which === $.ui.keyCode.ENTER) {
        this.addText();
      }
    };

    this.trackParagraph = function(target, event) {
      if(event.which === $.ui.keyCode.ENTER) {
        this.addParagraph();
      }
    };

    this.filterProposal = function(target) {
      var pattern = target.val();
      var result = $.grep(this.chache.items, function(item) {
        return item.title.toLowerCase().indexOf(pattern.toLowerCase()) >= 0;
      });
      this.render({ items: result });
    };

    this.events = {
      "click#.schedule-proposal!": this.schedule,
      "click#.schedule-paragraph": this.addParagraph,
      "click#.schedule-text": this.addText,
      "keyup##schedule-text": this.trackText,
      "keyup##schedule-paragraph": this.trackParagraph,
      "keyup##filter-proposals": this.filterProposal
    };

    this.init();

  }

  $(function() {

    if($("#opengever_meeting_meeting").length) {
      var meetingController = new MeetingController();
      var agendaItemController = new AgendaItemController();
      var proposalsController = new ProposalController();

      proposalsController.connectedTo = [agendaItemController];
      agendaItemController.connectedTo = [proposalsController];
    }


    $(global.document).on("notify", function() {
      var notifyContainer = new global.StickyHeading({ selector: "#columns", clone: false, fix: false });
      notifyContainer.onSticky(function() { $(".notifyjs-corner").addClass("sticky"); });
      notifyContainer.onNoSticky(function() { $(".notifyjs-corner").removeClass("sticky"); });
    });
  });

}(window, jQuery));
