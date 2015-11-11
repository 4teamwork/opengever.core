$(document).ready(function() {
  var scrollSpy = $("#scrollspy");

  $("#opengever_meeting_protocol textarea").autosize();

  var scrollspy = new Scrollspy({ selectParent: true });

  var navigation = $(".protocol-navigation");

  var headings = new StickyHeading({ selector: "#opengever_meeting_protocol .protocol_title" });
  var labels = new StickyHeading({ selector: "#opengever_meeting_protocol .agenda_items label", fix: false, dependsOn: headings});
  var collapsible = StickyHeading({ selector: "#opengever_meeting_protocol .collapsible", clone: false});

  var currentOffset;

  collapsible.onSticky(function() {
    navigation.addClass("sticky");
  });

  headings.onNoSticky(function() {
    navigation.removeClass("sticky");
    $(".metadata .fields").css("position", "static");
  });

  headings.onSticky(function(heading) {
    navigation.addClass("sticky");
    currentOffset = heading.clone.outerHeight();
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
    //Manual offset from sticky hading to label
    scrollspy.offset(currentOffset + 20);
    scrollspy.select($("#" + fadingOut.node.attr("for") + "-anchor"));
  });

  scrollspy.onScroll(function(target, toElement) {
    if(target.hasClass("expandable")) {
      scrollspy.expand(target);
    }
    moveCaretToEnd(toElement[0])
    //Trigger Scrolltop event with 3 pixel more for triggering the first item to be selected
    $(window).scrollTop($(window).scrollTop() + 3)
  });

  function moveCaretToEnd(el) {
    if (typeof el.selectionStart == "number") {
        el.selectionStart = el.selectionEnd = el.value.length;
    } else if (el.createTextRange) {
        var range = el.createTextRange();
        range.collapse(false);
    }
    el.focus();
  }

});