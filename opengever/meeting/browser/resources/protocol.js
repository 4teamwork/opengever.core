$(document).ready(function() {
  var scrollSpy = $("#scrollspy");

  $("#opengever_meeting_protocol textarea").autosize();

  var stickyHeadingInstance = stickyHeading("#opengever_meeting_protocol .protocol_title");

  var currentTarget;

  if(stickyHeadingInstance) {
    stickyHeadingInstance.onNoSticky(function() {
      scrollSpy.css("position", "static");
      $(".metadata .fields").css("position", "static");
    });

    stickyHeadingInstance.onSticky(function(heading) {
      scrollSpy.css("position", "fixed");
      $(".metadata .fields").css("position", "fixed");
      if(currentTarget && !currentTarget.hasClass("protocol_title")) {
        $('html, body').scrollTop(currentTarget.offset().top - (heading.node.height() + 30));
        currentTarget = null;
      }
    });

    stickyHeadingInstance.onCollision(function() {
      scrollSpy.css("position", "fixed");
      $(".metadata .fields").css("position", "fixed");
    });
  }

  function moveCaretToEnd(el) {
    if (typeof el.selectionStart == "number") {
        el.selectionStart = el.selectionEnd = el.value.length;
    } else if (el.createTextRange) {
        var range = el.createTextRange();
        range.collapse(false);
    }
    el.focus();
  }

  $("#scrollspy a").click(function(event) {
    event.preventDefault();
    var anchor = $(this).attr("href");
    var target = $(anchor);
    moveCaretToEnd(target[0]);
    currentTarget = target;
    $('html, body').scrollTop(target.offset().top);
  });

});