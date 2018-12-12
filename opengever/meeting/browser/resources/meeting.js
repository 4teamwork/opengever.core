(function(global, $, Controller, Pin, HBS) {

  "use strict";

  HBS.registerHelper({
    or: function (v1, v2) {return v1 || v2;}
  });

  function MeetingController() {

    Controller.call(this);

    var self = this;

    var dialog = $( "#confirm_close_meeting" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 }
    }).data("overlay");

    var cancelMeetingDialog = $( "#confirm_cancel_meeting" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
    }).data("overlay");

    var generateProtocolDialog = $( "#confirm_generate_protocol" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
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

    this.showCancelMeetingDialog = function(target) {
      self.currentItem = target;
      cancelMeetingDialog.load();
    };

    this.closeCancelMeetingDialog = function() {
      cancelMeetingDialog.close();
    };

    this.cancelMeeting = function() {
      return $.post(self.currentItem.attr("href")).always(function(){
        cancelMeetingDialog.close();
      }).done(function(data) {
        if (data.redirectUrl){
          window.location = data.redirectUrl;
        }
      });
    };

    this.showGenerateProtocolDialog = function(target) {
      self.currentItem = target;
      generateProtocolDialog.load();
    };

    this.closeGenerateProtocolDialog = function() {
      generateProtocolDialog.close();
    };

    this.generateProtocol = function() {
      window.location = self.currentItem.attr("href");
    };

    this.reopenMeeting = function(target) {
      return $.post(target.attr("href")).done(function(data) {
        if (data.redirectUrl){
          window.location = data.redirectUrl;
        }
      });
    };

    this.filterParticipants = function(target) {
      var filter_text = target.val().toLowerCase();
      $('.participant-list .participant').each(function() {
        if($(this).find('.fullname').text().toLowerCase().indexOf(filter_text) > -1) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    };

    this.clearParticipantsFilter = function(target) {
      $('input#participants-filter').val('').keyup().focus();
    };

    this.toggleParticipant = function(target, event) {
      if($(event.target).is('select, option, input, label')) {
        return;
      }

      if(!target.hasClass('editable')) {
        return;
      }

      if(!target.hasClass('folded')) {
        target.addClass('folded');
        return;
      }

      $('.participant-list .participant').addClass('folded');
      target.removeClass('folded');

      var current_role = target.find('div.role').data('rolename');
      target.find('select.role').val(current_role);

      var present = target.find('div.presence').hasClass('present');
      target.find('input.excused').selected(!present);

      target.find('.saving').removeClass('saving');
      target.find('.saved').removeClass('saved');
      target.find('.saving-failed').removeClass('saving-failed');
    };

    this.changeParticipantRole = function(target) {
      var wrapper = target.parents('.select-role-wrapper:first');
      this.showSavingChangeIcon(wrapper);
      var data = {member_id: target.data().member_id, role: target.val()};
      return $.post(target.data().url, data).done(function(response) {
        if(response.proceed !== true) {
          self.showSavingFailedIcon(wrapper);
          return;
        }
        self.showChangeSavedIcon(wrapper);
        if (target.val()) {
          $('.participant div.role').each(function() {
            if($(this).data().rolename == target.val()) {
              $(this).text('').data('rolename', '');
            }
          });
        }
        wrapper.prevAll('div.role').
              text(target.find('option:selected').text()).
              data('rolename', target.val());
        self.updateParticipantRolesInByline();
      });
    };

    this.updateParticipantRolesInByline = function() {
      var presidency = null;
      var secretary = null;
      $('.participant').each(function() {
        if($(this).find('div.role').length === 0) {
          return;
        }
        var role = $(this).find('div.role').data().rolename;
        if(role == 'presidency') {
          presidency = $(this).find('div.fullname').text();
        } else if(role == 'secretary') {
          secretary = $(this).find('div.fullname').text();
        }
      });
      if(presidency) {
        $('.byline-presidency').removeClass('hidden').find('span.value').text(presidency);
      } else {
        $('.byline-presidency').addClass('hidden');
      }
      if(secretary) {
        $('.byline-secretary').removeClass('hidden').find('span.value').text(secretary);
      } else {
        $('.byline-secretary').addClass('hidden');
      }
    };

    this.changeParticipantPresence = function(target) {
      var wrapper = target.parents('.change_presence:first');
      var present = !target.is(':checked');
      this.showChangeSavedIcon(wrapper);
      var data = {member_id: target.data().member_id, present: present};
      return $.post(target.data().url, data).done(function(response) {
        if(response.proceed !== true) {
          self.showSavingFailedIcon(wrapper);
          return;
        }
        if(present) {
          wrapper.prevAll('div.presence').
                removeClass('not-present').
                addClass('present');
        } else {
          wrapper.prevAll('div.presence').
                removeClass('present').
                addClass('not-present');
        }
        self.showChangeSavedIcon(wrapper);
      });
    };

    this.showSavingChangeIcon = function(target) {
      target.addClass('saving');
    };

    this.showChangeSavedIcon = function(target) {
      target.removeClass('saving');
      target.addClass('saved');
      window.setTimeout(function() { target.removeClass('saved'); }, 10000);
    };

    this.showSavingFailedIcon = function(target) {
      target.removeClass('saving');
      target.addClass('saving-failed');
      window.setTimeout(function() { target.removeClass('saving-failed'); }, 10000);
    };

    this.events = [
      {
        method: "click",
        target: "#pending-closed, #held-closed, .close-meeting a",
        callback: this.openModal,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#closed-held, .reopen-meeting",
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
      },
      {
        method: "click",
        target: "#confirm_cancel_meeting .confirm",
        callback: this.cancelMeeting,
        options: {
          prevent: false,
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: "#confirm_cancel_meeting .decline",
        callback: this.closeCancelMeetingDialog,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#pending-cancelled, .cancel-meeting a",
        callback: this.showCancelMeetingDialog,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: "#confirm_generate_protocol .confirm",
        callback: this.generateProtocol,
        options: {
          prevent: false,
          update: true,
          loading: true
        }
      },
      {
        method: "click",
        target: "#confirm_generate_protocol .decline",
        callback: this.closeGenerateProtocolDialog,
        options: {
          update: true
        }
      },
      {
        method: "click",
        target: ".document-actions #generate_protocol_with_confirm",
        callback: this.showGenerateProtocolDialog,
        options: {
          update: true
        }
      },
      {
        method: "keyup",
        target: "input#participants-filter",
        callback: this.filterParticipants
      },
      {
        method: "click",
        target: "a#clear-participants-filter",
        callback: this.clearParticipantsFilter,
        options: {
          prevent: true
        }
      },
      {
        method: "click",
        target: ".participant-list .participant",
        callback: this.toggleParticipant,
        options: {
          prevent: false
        }
      },
      {
        method: "change",
        target: ".participant-list .participant select.role",
        callback: this.changeParticipantRole
      },
      {
        method: "change",
        target: ".participant-list .participant .change_presence input.excused",
        callback: this.changeParticipantPresence
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
      mask: { loadSpeed: 0 },
      onBeforeLoad: function() {
        var title = self.currentItem.parents("tr").find(".proposal_title").text();
        $('#confirm_unschedule_item_title').text(title);
      },
    }).data("overlay");

    var deleteDialog = $( "#confirm_delete" ).overlay({
      speed: 0,
      closeSpeed: 0,
      mask: { loadSpeed: 0 },
      onBeforeLoad: function() {
        var title = self.currentItem.parents("tr").find(".proposal_title").text();
        $('#confirm_delete_item_title').text(title);
      },
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

    var renameAgendaItemDialog = new function() {
      var self = this;
      self.url = null;
      self.row = null;
      self.titlePane = null;
      self.descriptionPane = null;
      self.title_field = $('#agenda_item_title_field');
      self.description_field = $('#agenda_item_description_field');
      self.overlay = $('#rename_agenda_item_dialog').overlay({
        speed: 0,
        closeSpeed: 0,
        mask: { loadSpeed: 0 },
        closeOnClick: false,
        closeOnEsc: true,
        onLoad: function() {
          self.title_field.focus();
        },
        onClose: function() {
          self.row = null;
          self.titlePane = null;
          self.title_field.val('');
          self.description_field.val('');
        }
      }).data("overlay");

      self.open = function(target) {
        self.url = target.attr('href');
        self.row = target.parents('tr:first');
        self.titlePane = $('.proposal_title>a, .proposal_title', self.row);
        self.descriptionPane = $('.proposal_description', self.row);
        self.title_field.val(self.titlePane.first().text().trim());
        self.description_field.val(self.descriptionPane.first().text().trim());
        self.overlay.load();
      };

      self.submit = function() {
        var data = {title: self.title_field.val().trim(), description: self.description_field.val().trim()};
        return $.post(self.url, data).always(function(response) {
          self.overlay.close();
        });
      };

      self.cancel = function() {
        if (typeof(self.overlay) !== 'undefined') {
          self.overlay.close();
        }
      };
    };

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
    if ($("#navigationTemplate").length > 0) {
      this.navigationTemplate = HBS.compile($("#navigationTemplate").html());
    }


    this.fetch = function() { return $.get(viewlet.data().listAgendaItemsUrl); };

    this.render = function(data) {
      self.renderNavigation(data);
      return self.template({
        agendaitems: data.items,
        editable: viewlet.data().editable,
        agendalist_editable: viewlet.data().agendalist_editable
      });
    };

    this.renderNavigation = function(data) {
      if (typeof this.navigationTemplate === 'undefined') {
        return;
      }

      $('.meeting-navigation').html(this.navigationTemplate({agendaitems: data.items}));
      this.updateNavigationScrollArea();
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
        $('#confirm_create_excerpt .confirm').removeClass("loading");
      }
      renameAgendaItemDialog.cancel();
    };

    this.updateSortOrder = function() {
      var numbers = $.map($("tr", this.outlet), function(row) { return $(row).data().uid; });
      return $.post(viewlet.data().updateAgendaItemOrderUrl,
                    { sortOrder: JSON.stringify(numbers) }).fail(function() {
                      self.refresh();
                    });
    };

    this.onRender = function() {
      this.outlet.sortable(sortableSettings);
      $(document).trigger("agendaItemsReady");
      this.updateCloseTransitionActionState();
    };

    this.onUpdateFail = function(data) { self.messageFactory.shout(data.messages); };

    this.toggleAttachements = function(target) { target.parents("tr").toggleClass("expanded"); };

    this.decide = function(target) {
      this.currentDecideTarget = target;
      if(viewlet.data().agendalist_editable) {
        holdDialog.load();
        return null;
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
        self.updateCloseTransitionActionState();
      });
    };

    this.declineDecide = function() { holdDialog.close(); };

    this.reopen = function(target){
      return $.post(target.attr("href")).done(function() {
        self.updateCloseTransitionActionState();
      }).fail(function () {
        self.update();
      });
    };

    this.revise = function(target){
      return $.post(target.attr("href")).always(function() {
        self.updateCloseTransitionActionState();
      }).fail(function () {
        self.update();
      });
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
      return $.post(link, $('#confirm_create_excerpt form').serialize()).always(function() {
        self.closeModal();
      });
    };

    this.returnExcerpt = function() {
      self = this;
      return $.get(this.currentItem.attr("href")).always(function() {
        self.closeModal();
      });
    };

    this.navigationClick = function(target) {
      $('html, body').animate({
        scrollTop: $(target.attr('href')).offset().top
      }, 150);
    };

    this.updateNavigationScrollArea = function() {
      /** When necessary, make the navigation scrollable, so that the
          meeting process area also has enough space. **/
      $('.meeting-navigation').css('max-height', '');
      /** Let the navigation have the screen size minues the size of the
          meeting process div. **/
      var navigation_max_height = $(window).height() - $('.meeting-process').outerHeight();
      if($('.meeting-navigation').height() > navigation_max_height) {
        $('.meeting-navigation').addClass('scroll');
      } else {
        $('.meeting-navigation').removeClass('scroll');
      }
      $('.meeting-navigation').css('max-height', navigation_max_height);

      /** Set the container height so that stickyness works. */
      $('.panes').height(null);
      $('.panes').height(Math.max($('.panes').height(),
                                  $('#content-core').height()));
    };

    this.updateCloseTransitionActionState = function() {
      if($("[completed='false']").length > 0) {
        $('.close-meeting').addClass('disabled');
        $('.cancel-meeting').hide();
      } else {
        $('.close-meeting').removeClass('disabled');
        $('.cancel-meeting').show();
      }
      this.updateNavigationScrollArea();
    };

    this.editMenuFor = function(toggle) {
      return $(toggle).parents('.agenda-item-actions:first').find('ul.editing-menu');
    };

    this.toggleEditMenu = function(target) {
      this.editMenuFor(target).toggleClass('opened');
    };

    this.closeEditMenues = function(target, event) {
      if($(event.target).is('a.editing-menu') &&
         this.editMenuFor(event.target).is('.opened')) {
        /* User is trying to close the currently opened menu by using the toggle.
           Let's not interfere. */
        return;
      }
      $('ul.editing-menu.opened').removeClass('opened');
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
        target: ".rename-agenda-item",
        callback: renameAgendaItemDialog.open
      },
      {
        method: "submit",
        target: "#rename_agenda_item_dialog form",
        callback: renameAgendaItemDialog.submit,
        options: {
          update: true,
          loading: true,
          prevent: true
        }
      },
      {
        method: "click",
        target: "#rename_agenda_item_dialog .cancel",
        callback: renameAgendaItemDialog.cancel
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
      },
      {
        method: "click",
        target: ".meeting-navigation a",
        callback: this.navigationClick,
        options: {
          prevent: false
        }
      },
      {
        method: "click",
        target: "a.editing-menu",
        callback: this.toggleEditMenu
      },
      {
        method: "mouseup",
        target: document,
        callback: this.closeEditMenues
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
      var title = $("#schedule-paragraph-title");
      var description = $("#schedule-paragraph-description");
      var button = $(".schedule-paragraph");
      button.addClass("loading");

      return $.post(button.first().data().url, {
          title: title.val(),
          description: description.val(),
          }).done(function() {
            if(title.val()){
              title.val("");
              description.val("");
              }
            self.updateConnected();
        }).always(function() {
            button.removeClass("loading");
        });
    };

    this.addText = function() {
      var template_id = $(
          "#ad-hoc-agenda-item-proposal-templates input[name=selected_ad_hoc_agenda_item_template]:checked"
      ).attr('value');
      var title = $("#schedule-title");
      var description = $("#schedule-description");
      var button = $(".schedule-text");
      button.addClass("loading");
      return $.post(button.first().data().url, {
          title: title.val(),
          description: description.val(),
          template_id: template_id,
        }).done(function() {
            if(title.val()){
              title.val("");
              description.val("");
              }
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
        target: "#schedule-title",
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

    $(global.document).on("notify", function() {
      var notifyContainer = Pin("#columns", null, { pin: false });
      notifyContainer.onPin(function() { $(".notifyjs-corner").addClass("sticky"); });
      notifyContainer.onRelease(function() { $(".notifyjs-corner").removeClass("sticky"); });
    });
  });

}(window, window.jQuery, window.Controller, window.Pin, window.Handlebars));
