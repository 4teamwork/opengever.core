(function(global) {

  "use strict";

  function ProtocolController() {

    global.Controller.call(this);

    var currentMeeting = $(".protocol-navigation").data().meeting;
    var createdAt = new Date($(".protocol-navigation").data().modified).getTime();

    var protocolSynchronizer = new global.Synchronizer({ target: "textarea" });
    var meetingStorage = new global.MeetingStorage(currentMeeting);

    var updateAutosize = function() {
      global.autosize.update(document.querySelectorAll(protocolSynchronizer.options.target));
    };

    var parseProposal = function(expression) { return expression.split("-"); };

    var syncProposal = function(target) {
      var proposalExpression = parseProposal(target.id);
      var text = target.value;
      meetingStorage.addOrUpdateUnit(proposalExpression[1], proposalExpression[2], text);
      meetingStorage.push();
    };

    protocolSynchronizer.onSync(syncProposal);
    protocolSynchronizer.observe();

    meetingStorage.pull();

    if(createdAt < meetingStorage.currentMeeting.revision) {
      meetingStorage.restore();
      updateAutosize();
    }

    this.saveProtocol = function(target) {
      var payload = target.parents("form").serializeArray();
      payload.push({ name: "form.buttons.save", value: $("#form-buttons-save").val() });
      var action = target.attr("action");
      return $.ajax({
        type: "POST",
        url: action,
        data: payload,
        dataType: "json"
      }).done(function(data) {
        meetingStorage.deleteCurrentMeeting();
        window.location = data.redirectUrl;
      });
    };

    this.events = {
      "click##form-buttons-save$": this.saveProtocol,
    };

    this.init();

  }

  function init() {

    global.autosize($("#opengever_meeting_protocol textarea"));

    var scrollspy = new global.Scrollspy({ selector: ".navigation" });

    var navigation = $(".protocol-navigation");

    navigation.css("left", navigation.offset().left);

    var headings = new global.StickyHeading({ selector: "#opengever_meeting_protocol .protocol_title" });
    var labels = new global.StickyHeading({ selector: "#opengever_meeting_protocol .agenda_items label", fix: false, dependsOn: headings});
    var collapsible = new global.StickyHeading({ selector: "#opengever_meeting_protocol .collapsible", clone: false});

    function moveCaretToEnd(el) {
      if (typeof el.selectionStart === "number") {
          el.selectionStart = el.selectionEnd = el.value.length;
      } else if (el.createTextRange) {
          var range = el.createTextRange();
          range.collapse(false);
      }
      el.focus();
    }

    scrollspy.onBeforeScroll(function(target) {
      if(target.hasClass("expandable") && !target.hasClass("paragraph")) {
        scrollspy.options.offset = target.outerHeight() + 60;
      } else if (target.hasClass("paragraph")) {
        scrollspy.options.offset = 0;
      }
    });

    collapsible.onSticky(function() { navigation.addClass("sticky"); });

    headings.onNoSticky(function() {
      navigation.removeClass("sticky");
      $(".metadata .fields").css("position", "static");
    });

    headings.onSticky(function(heading) {
      navigation.addClass("sticky");
      $(".metadata .fields").css("position", "fixed");
      scrollspy.expand($("#" + heading.node.attr("id") + "-anchor"));
      scrollspy.select($("#" + heading.node.attr("id") + "-anchor"));
    });

    headings.onCollision(function() {
      navigation.addClass("sticky");
      $(".metadata .fields").css("position", "fixed");
    });

    labels.onSticky(function(label) {
      scrollspy.select($("#" + label.node.attr("for") + "-anchor"));
    });
    labels.onCollision(function(fadingIn, fadingOut) {
      scrollspy.select($("#" + fadingOut.node.attr("for") + "-anchor"));
    });

    scrollspy.onScroll(function(target, toElement) {
      if(target.hasClass("expandable")) {
        scrollspy.expand(target);
      }
      moveCaretToEnd(toElement[0]);
    });

    var protocolController = new ProtocolController();

  }

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      init();
    }
  });

}(window));
