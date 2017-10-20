(function(global, $, Controller, EditboxController, Pin) {

  "use strict";

  function MeetingController() {

    Controller.call(this);

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
      return $.post(self.currentItem.attr("href")).always(function(){
        dialog.close();
      }).done(function(data) {
        if (data.redirectUrl){
          window.location = data.redirectUrl;
        }
      });
    };

    this.closeModal = function() { dialog.close(); };

    this.reopenMeeting = function(target) {
      return $.post(target.attr("href")).done(function(data) {
        if (data.redirectUrl){
          window.location = data.redirectUrl;
        }
      });
    };

    this.events = [
      {
        method: "click",
        target: "#pending-closed",
        callback: this.openModal,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#held-closed",
        callback: this.openModal,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#closed-held",
        callback: this.reopenMeeting,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#confirm_close_meeting .confirm",
        callback: this.closeMeeting,
        options: {
          prevent: false,
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: "#confirm_close_meeting .decline",
        callback: this.closeModal,
        options: {
          update: true
        }
      }
    ];

    this.init();

  }

  function AgendaItemController(options) {

    var self = this;
    var viewlet = $("#opengever_meeting_meeting");

    var unscheduleDialog = $( "#confirm_unschedule" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    var deleteDialog = $( "#confirm_delete" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    var holdDialog = $( "#confirm_hold_meeting" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
      closeOnClick: false,
      closeOnEsc: false
    }).data("overlay");

    var returnExcerptDialog = $("#confirm_return_excerpt").overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
      closeOnClick: false,
      closeOnEsc: false
    }).data("overlay");

    var createExcerptDialog = $('#confirm_create_excerpt').overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
      closeOnClick: false,
      closeOnEsc: false,
      onBeforeLoad: function() {
        $('#excerpt_title').val(self.currentItem.data().defaultTitle);
      },
      onLoad: function() {
        $('#excerpt_title').focus().select();
      }
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

    Controller.call(this, $("#agendaitemsTemplate").html(), $("#agenda_items tbody"), options);

    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) {
      return self.template({
        agendaitems: data.items,
        editable: viewlet.data().editable,
        agendalist_editable: viewlet.data().agendalist_editable
      });
    };

    this.openModal = function(target) {
      this.currentItem = target;
      if(target.parents("tr").hasClass("proposal")) {
        unscheduleDialog.load();
      } else {
        deleteDialog.load();
      }
    };

    this.confirmReturnExcerpt = function(target) {
      this.currentItem = target;
      returnExcerptDialog.load();
    };

    this.unschedule = function() {
      this.closeModal();
      return $.post(this.currentItem.attr("href"));
    };

    this.closeModal = function() {
      unscheduleDialog.close();
      deleteDialog.close();
      if (typeof(returnExcerptDialog) !== 'undefined') {
        returnExcerptDialog.close();
      }
      if (typeof(createExcerptDialog) !== 'undefined') {
        createExcerptDialog.close();
      }
    };

    this.updateSortOrder = function() {
      var numbers = $.map($("tr", this.outlet), function(row) { return $(row).data().uid; });
      return $.post(viewlet.data().updateAgendaItemOrderUrl,
                    { sortOrder: JSON.stringify(numbers) }).fail(function() {
                      self.refresh();
                    });
    };

    this.showEditbox = function(target) {
      var row = target.parents("tr");
      row.removeClass("expanded");
      var source_selectors = [
            /* Word: */
            ".title > span.proposal_title > a",
            ".title > span.proposal_title",
            /* Non-word: */
            ".title > span > a",
            ".title > span"
      ];
      var source_selector = source_selectors.filter(function(selector) {
        return $(selector, row).length > 0;
      })[0];
      var source = $(source_selector, row);

      new EditboxController({
        editbox: $(".edit-box", row),
        source: source,
        trigger: target
      });
    };

    this.onRender = function() {
      this.outlet.sortable(sortableSettings);
      $(document).trigger("agendaItemsReady");
    };

    this.onUpdateFail = function(data) { self.messageFactory.shout(data.messages); };

    this.toggleAttachements = function(target) { target.parents("tr").toggleClass("expanded"); };

    this.decide = function(target) {
      this.currentDecideTarget = target;
      if(viewlet.data().agendalist_editable) {
        holdDialog.load();
      }
      else {
        return this.confirmDecide(target);
      }
    };

    this.confirmDecide = function() {
      var holdDialogCancelButton = $("#confirm_hold_meeting .decline");
      holdDialogCancelButton.hide();
      return $.post(this.currentDecideTarget.attr("href")).always(function(){
        holdDialogCancelButton.show();
        holdDialog.close();
      }).done(function(data){
        if (data.redirectUrl){
          window.location = data.redirectUrl;
        }
      });
    };

    this.declineDecide = function() { holdDialog.close(); };

    this.reopen = function(target){
      return $.post(target.attr("href"));
    };

    this.revise = function(target){
      return $.post(target.attr("href"));
    };

    this.editDocument = function(target) {
      return $.get(target.attr("href")).done(function(response) {
        if(response.proceed === true) {
          window.location = response.officeConnectorURL;
          $(target).parents("tr").find(".proposal_document").addClass("checked-out");
        }
      });
    };

    this.openGenerateExcerptDialog = function(target) {
      this.currentItem = target;
      createExcerptDialog.load();
    };

    this.generateExcerpt = function(target, event) {
      var link = self.currentItem[0].href;
      self = this;
      return $.post(link, $('#confirm_create_excerpt form').serialize())
              .always(function() {
                self.closeModal();
              });
    }

    this.returnExcerpt = function() {
      self = this;
      return $.get(this.currentItem.attr("href")).always(function() {
        self.closeModal();
      });
    };

    this.events = [
      {
        method: "click",
        target: ".edit-document",
        callback: this.editDocument
      },
      {
        method: "click",
        target: ".delete-agenda-item",
        callback: this.openModal
      },
      {
        method: "click",
        target: ".edit-agenda-item",
        callback: this.showEditbox
      },
      {
        method: "click",
        target: ".decide-agenda-item",
        callback: this.decide,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".reopen-agenda-item",
        callback: this.reopen,
        options: {
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: ".revise-agenda-item",
        callback: this.revise,
        options: {
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: ".generate-excerpt",
        callback: this.openGenerateExcerptDialog,
        options: {
          prevent: true
        }
      },
      {
        method: "click",
        target: ".return-excerpt-btn",
        callback: this.confirmReturnExcerpt,
        options: {
          prevent: true
        }
      },
      {
        method: "click",
        target: "#confirm_return_excerpt .confirm",
        callback: this.returnExcerpt,
        options: {
          prevent: false,
          loading: true,
          update: true
        }
      },
      {
        method: "click",
        target: "#confirm_create_excerpt .confirm",
        callback: this.generateExcerpt,
        options: {
          prevent: true,
          loading: true,
          update: true
        }
      },
      {
        method: "sortupdate",
        target: "#agenda_items tbody",
        callback: this.updateSortOrder,
        options: {
          prevent: false,
          update: true
        }
      },
      {
        method: "click",
        target: ".toggle-attachements",
        callback: this.toggleAttachements
      },
      {
        method: "click",
        target: "#confirm_unschedule .confirm, #confirm_delete .confirm",
        callback: this.unschedule,
        options: {
          prevent: false,
          update: true
        }
      },
      {
        method: "click",
        target: "#confirm_unschedule .decline, #confirm_delete .decline, #confirm_return_excerpt .decline, #confirm_create_excerpt .decline",
        callback: this.closeModal
      },
      {
        method: "click",
        target: "#confirm_hold_meeting .confirm",
        callback: this.confirmDecide,
        options: {
          prevent: false,
          loading: true
        }
      },
      {
        method: "click",
        target: "#confirm_hold_meeting .decline",
        callback: this.declineDecide
      }
    ];

    this.init();

  }

  function ProposalController(options) {

    var viewlet = $("#opengever_meeting_meeting");
    Controller.call(this, $("#proposalsTemplate").html(), $("#unscheduled_porposals"), options);
    var self = this;

    this.fetch = function() { return $.get(viewlet.data().listUnscheduledProposalsUrl); };

    this.render = function(data) { return self.template({ proposals: data.items }); };

    this.schedule = function(target) {
      return $.post(target.attr("href")).done(function() { $("#filter-proposals").val(""); });
    };

    this.addParagraph = function() {
      var input = $("#schedule-paragraph");
      var button = $(".schedule-paragraph");
      button.addClass("loading");
      return $.post(button.data().url, { title: input.val() }).done(function() {
        input.val("");
        self.updateConnected();
      }).always(function() {
        button.removeClass("loading");
      });
    };

    this.addText = function() {
      var input = $("#schedule-text");
      var button = $(".schedule-text");
      button.addClass("loading");
      return $.post(button.first().data().url, { title: input.val() }).done(function() {
        input.val("");
        self.updateConnected();
      }).always(function() {
        button.removeClass("loading");
      });
    };

    this.trackText = function(target, event) {
      if(event.which === $.ui.keyCode.ENTER) {
        return this.addText();
      }
    };

    this.trackParagraph = function(target, event) {
      if(event.which === $.ui.keyCode.ENTER) {
        return this.addParagraph();
      }
    };

    this.filterProposal = function(target) {
      var pattern = target.val();
      var result = $.grep(self.cache.items, function(item) {
        return item.title.toLowerCase().indexOf(pattern.toLowerCase()) >= 0;
      });
      this.outlet.html(this.render({ items: result }));
    };

    this.events = [
      {
        method: "click",
        target: ".schedule-proposal",
        callback: this.schedule,
        options: {
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: ".schedule-paragraph",
        callback: this.addParagraph
      },
      {
        method: "click",
        target: ".schedule-text",
        callback: this.addText
      },
      {
        method: "keyup",
        target: "#schedule-text",
        callback: this.trackText
      },
      {
        method: "keyup",
        target: "#schedule-paragraph",
        callback: this.trackParagraph
      },
      {
        method: "keyup",
        target: "#filter-proposals",
        callback: this.filterProposal
      }
    ];

    this.init();

  }

  function CommitteeController() {

    Controller.call(this);

    var title = $("#form-widgets-title");
    var autoUpdate = true;
    var initialTitle = title.val();

    var formatDate = function(date) { return $.datepicker.formatDate("dd.mm.yy", date); };

    var applyTimezone = function(date) {
      return new Date(date.setTime(date.getTime() + (date.getTimezoneOffset() * 60 * 1000)));
    };

    function applyDate(date) {
      if (!autoUpdate) {
        return false;
      }
      title.val(initialTitle + ", " + formatDate(date));
    }

    this.trackDate = function(target, event) { applyDate(applyTimezone(event.date)); };

    this.unbindDate = function() { autoUpdate = false; };

    this.events = [
      {
        method: "changeDate",
        target: "#formfield-form-widgets-start .spv-datetime-widget",
        callback: this.trackDate
      },
      {
        method: "input",
        target: "#form-widgets-title",
        callback: this.unbindDate
      }
    ];

    this.init();
    applyDate(new Date());

  }

  $(function() {

    if($("#opengever_meeting_meeting").length) {
      new MeetingController();
      var agendaItemController = new AgendaItemController();
      var proposalsController = new ProposalController();

      proposalsController.connectedTo = [agendaItemController];
      agendaItemController.connectedTo = [proposalsController];

      window.addEventListener("pageshow", function() {
        agendaItemController.update();
      });

      $('#opengever_meeting_meeting .sidebar > ul.formTabs').tabs(
            '.sidebar .panes > div', {current: 'selected'});
    }

    if ($(".template-add-meeting").length) {
      new CommitteeController();
    }

    $(global.document).on("notify", function() {
      var notifyContainer = Pin("#columns", null, { pin: false });
      notifyContainer.onPin(function() { $(".notifyjs-corner").addClass("sticky"); });
      notifyContainer.onRelease(function() { $(".notifyjs-corner").removeClass("sticky"); });
    });
  });

}(window, window.jQuery, window.Controller, window.EditboxController, window.Pin));
