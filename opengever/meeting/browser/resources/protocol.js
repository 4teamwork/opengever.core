(function(global, $, MeetingStorage, Pin, Synchronizer, Controller, Scrollspy, SelectAutocomplete) {

  "use strict";

  function ProtocolController() {

    Controller.call(this);

    var root = $(":root");

    var headings;
    var labels;

    var saveButton = $("#form-buttons-save");
    var protocolControls = $("#protocol-controls");

    var currentMeeting = $(".protocol-navigation").data().meeting;
    var protocolSynchronizer = new Synchronizer({
    var createdAt = new Date($(".protocol-navigation").data().modified).getTime();

      target: "#content-core input, #content-core select, #content-core textarea",
      triggers: ["input", "change", "changeDate"]
    });

    var trixSynchronizer = new global.Synchronizer({
      target: "trix-editor",
      triggers: ["trix-change"]
    });

    var meetingStorage = new global.MeetingStorage(currentMeeting);

    var showHintForLocalChanges = function() {
      $("#form-buttons-cancel").val($("#button-value-discard").val());
      protocolControls.addClass("local-changes");
    };

    var showHintForConflictChanges = function() { root.addClass("conflict-changes"); };

    var parseProposal = function(expression) { return expression.split("-"); };

    var syncTrix = function(target) {
      var proposalExpression = parseProposal(target.inputElement.id);
      var html = JSON.stringify(target.editor);
      meetingStorage.addOrUpdateUnit(proposalExpression[1], proposalExpression[2], html);
      meetingStorage.push();
      showHintForLocalChanges();
      headings.refresh();
      labels.refresh();
    };

    var syncProposal = function() { showHintForLocalChanges(); };

    protocolSynchronizer.onSync(syncProposal);
    protocolSynchronizer.observe();

    trixSynchronizer.onSync(syncTrix);
    trixSynchronizer.observe();

    meetingStorage.pull();

    if(createdAt < meetingStorage.currentMeeting.revision) {
      meetingStorage.restore();
    }

    this.saveProtocol = function(target) {
      var form = target.parents("form");
      var payload = form.serializeArray();
      payload.push({ name: "form.buttons.save", value: saveButton.val() });
      var conflictValidator = function(data) {
        if(data.hasConflict) {
          showHintForConflictChanges();
        }
        return !data.hasConflict;
      };
      return this.request(form.attr("action"), {
        type: "POST",
        data: payload,
        validator: conflictValidator
      }).done(function(data) {
        if (data.redirectUrl !== undefined) {
          meetingStorage.deleteCurrentMeeting();
          window.location = data.redirectUrl;
        } else {
          // we stay on the same site. allow re-submit.
          $("#form-buttons-save").removeClass("submitting");
        }
      });
    };

    this.discardProtocol = function() { meetingStorage.deleteCurrentMeeting(); };

    this.initScrollspy = function() {
      var scrollspy = Scrollspy(".navigation > ul");

      headings = Pin("#opengever_meeting_protocol .protocol_title", "trix-toolbar");
      labels = Pin("#opengever_meeting_protocol .agenda_items label", null, { pin: false });
      Pin(".protocol-navigation", null, { pin: false });

      headings.onRelease(function() { scrollspy.reset(); });

      headings.onPin(function(item) { scrollspy.select($("#" + item.element.attr("id") + "-anchor")); });

      labels.onPin(function(item) { scrollspy.select($("#" + item.element.attr("for") + "-anchor")); });
    };

    this.events = [
      {
        method: "click",
        target: "#form-buttons-save",
        callback: this.saveProtocol
      },
      {
        method: "click",
        target: "#form-buttons-cancel",
        callback: this.discardProtocol,
        options: {
          prevent: false
        }
      },
      {
        method: "ready",
        target: document,
        callback: this.initScrollspy
      }
    ];

    this.init();

    if(meetingStorage.currentMeeting.revision) {
      showHintForLocalChanges();
    }
  }

  function TrixController() {

    global.Controller.call(this);

    this.activateToolbar = function(toolbar) {
      $("trix-toolbar").removeClass("active");
      toolbar.addClass("active");
    };

    this.attachToolbar = function(target) { this.activateToolbar($("#" + target.attr("toolbar"))); };

    this.events = [
      {
        method: "click",
        target: "trix-editor",
        callback: this.attachToolbar
      }
    ];

    this.init();

  }

  var trixController = new TrixController();

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      var protocolController = new ProtocolController();
    }
    if($(".template-opengever-meeting-proposal, .portaltype-opengever-meeting-submittedproposal.template-edit, .portaltype-opengever-meeting-proposal.template-edit").length) {
      Pin("trix-toolbar");
    }
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      var autocompleteSelects = new global.SelectAutocomplete();
    }
  });

}(window, jQuery, window.MeetingStorage, window.Pin, window.Synchronizer, window.Controller, window.Scrollspy, window.SelectAutocomplete));
