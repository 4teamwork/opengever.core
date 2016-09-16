(function(global, $, MeetingStorage, Pin, Synchronizer, Controller, Scrollspy, SelectAutocomplete) {

  "use strict";

  function ProtocolController() {

    Controller.call(this);

    var root = $(":root");

    var headings;
    var labels;

    $(document).on("editor.save", function() {
      showHintForLocalChanges();
      headings.refresh();
      labels.refresh();
    });

    var saveButton = $("#form-buttons-save");
    var protocolControls = $("#protocol-controls");

    var protocolSynchronizer = new Synchronizer({
      target: "#content-core input, #content-core select, #content-core textarea",
      triggers: ["input", "change", "changeDate"]
    });

    var showHintForLocalChanges = function() {
      $("#form-buttons-cancel").val($("#button-value-discard").val());
      protocolControls.addClass("local-changes");
    };

    var showHintForConflictChanges = function() { root.addClass("conflict-changes"); };

    var syncProposal = function() { showHintForLocalChanges(); };

    protocolSynchronizer.onSync(syncProposal);
    protocolSynchronizer.observe();

    function createdAt() { return new Date($(".protocol-navigation").data().modified).getTime(); }

    function restore() {
      var meetingStorage = MeetingStorage.getInstance();
      if(createdAt() < meetingStorage.get().revision) {
        $.each(meetingStorage.get(), function(proposalId, proposal) {
          $.each(proposal, function(sectionName, section) {
            $("#agenda_item-" + proposalId + "-" + sectionName).val(section);
            $("#proxy-agenda_item-" + proposalId + "-" + sectionName).html(section);
          });
        });
        showHintForLocalChanges();
      }
    }

    this.discardProtocol = function() { MeetingStorage.getInstance().destroy(); };

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
          MeetingStorage.getInstance().destroy();
          window.location = data.redirectUrl;
        } else {
          // we stay on the same site. allow re-submit.
          $("#form-buttons-save").removeClass("submitting");
        }
      });
    };

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

    restore();
  }

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      new ProtocolController();
    }
    if($(".template-opengever-meeting-proposal, .portaltype-opengever-meeting-submittedproposal.template-edit, .portaltype-opengever-meeting-proposal.template-edit").length) {
      Pin("trix-toolbar");
    }
    if($(".template-add-membership, .template-opengever-meeting-proposal, .portaltype-opengever-meeting-proposal.template-edit").length) {
      new SelectAutocomplete();
    }
  });

}(window, jQuery, window.MeetingStorage, window.Pin, window.Synchronizer, window.Controller, window.Scrollspy, window.SelectAutocomplete));
