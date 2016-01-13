(function(global, $) {

  "use strict";

  function ProtocolController() {

    global.Controller.call(this);

    var saveButton = $("#form-buttons-save");
    var protocolControls = $("#protocol-controls");

    var currentMeeting = $(".protocol-navigation").data().meeting;
    var createdAt = new Date($(".protocol-navigation").data().modified).getTime();

    var protocolSynchronizer = new global.Synchronizer({ target: "input, select, textarea", triggers: ["input", "change"] });
    var trixSynchronizer = new global.Synchronizer({ target: "trix-editor", triggers: ["trix-change"] });
    var meetingStorage = new global.MeetingStorage(currentMeeting);

    var showHintForLocalChanges = function() {
      $("#form-buttons-cancel").val($("#button-value-discard").val());
      protocolControls.addClass("local-changes");
    };

    var parseProposal = function(expression) { return expression.split("-"); };

    var syncTrix = function(target) {
      var proposalExpression = parseProposal(target.inputElement.id);
      var html = JSON.stringify(target.editor);
      meetingStorage.addOrUpdateUnit(proposalExpression[1], proposalExpression[2], html);
      meetingStorage.push();
      showHintForLocalChanges();
    };

    var syncProposal = function() {
      showHintForLocalChanges();
    };

    protocolSynchronizer.onSync(syncProposal);
    protocolSynchronizer.observe();

    trixSynchronizer.onSync(syncTrix);
    trixSynchronizer.observe();

    meetingStorage.pull();

    if(createdAt < meetingStorage.currentMeeting.revision) {
      meetingStorage.restore();
    }

    this.saveProtocol = function(target) {
      var payload = target.parents("form").serializeArray();
      payload.push({ name: "form.buttons.save", value: saveButton.val() });
      return $.post(target.attr("action"), payload)
              .done(function(data) {
              meetingStorage.deleteCurrentMeeting();
              window.location = data.redirectUrl;
             });
    };

    this.discardProtocol = function() { meetingStorage.deleteCurrentMeeting(); };

    this.events = {
      "click##form-buttons-save": this.saveProtocol,
      "click##form-buttons-cancel$": this.discardProtocol
    };

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

    this.attachToolbar = function(target) {
      this.activateToolbar($("#" + target.attr("toolbar")));
    };

    this.events = {
      "click#trix-editor": this.attachToolbar
    };

    this.init();

  }

  var trixController = new TrixController();

  function init() {

    var protocolController = new ProtocolController();

    var scrollspy = new global.Scrollspy({ selector: ".navigation" });

    var navigation = $(".protocol-navigation");

    navigation.css("left", navigation.offset().left);

    var headings = new global.StickyHeading({ selector: "#opengever_meeting_protocol .protocol_title" });
    var labels = new global.StickyHeading({ selector: "#opengever_meeting_protocol .agenda_items label", fix: false, dependsOn: headings});
    var collapsible = new global.StickyHeading({ selector: "#opengever_meeting_protocol .collapsible", clone: false});

    scrollspy.onBeforeScroll(function(target, anchor) { scrollspy.options.offset = anchor.siblings("h2.clone").height() + 40; });

    collapsible.onSticky(function() { navigation.addClass("sticky"); });

    headings.onNoSticky(function() { navigation.removeClass("sticky"); });

    headings.onSticky(function(heading) {
      navigation.addClass("sticky");
      scrollspy.expand($("#" + heading.node.attr("id") + "-anchor"));
      scrollspy.select($("#" + heading.node.attr("id") + "-anchor"));
    });

    headings.onCollision(function() { navigation.addClass("sticky"); });

    labels.onSticky(function(label) { scrollspy.select($("#" + label.node.attr("for") + "-anchor")); });

    labels.onCollision(function(fadingIn, fadingOut) { scrollspy.select($("#" + fadingOut.node.attr("for") + "-anchor")); });

    scrollspy.onScroll(function(target, anchor) {
      trixController.activateToolbar($("#" + anchor.attr("id") + "-toolbar"));
      if(target.hasClass("expandable")) {
        scrollspy.expand(target);
      }
    });


  }

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      init();
    }
  });

}(window, jQuery));
