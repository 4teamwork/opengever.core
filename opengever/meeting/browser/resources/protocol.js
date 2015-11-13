(function(global) {

  "use strict";

  function init() {

    $("#opengever_meeting_protocol textarea").autosize();

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
      if(target.hasClass("expandable")) {
        scrollspy.options.offset = target.outerHeight() + 60;
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
  }

  $(function() {
    if($("#opengever_meeting_protocol").length) {
      init();
    }
  });

}(window));
