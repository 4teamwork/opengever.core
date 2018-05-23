/*
This is a reimplementation of plones dropdown.

This implementation should determine if a menu should be opened
up or down.
*/

(function(global, $, origToggleMenuHandler, origActionMenuMouseOver, origHideAllMenus){

  function setArrow(trigger, dir) {
    var arrow = trigger.find('.arrowDownAlternative');
    if (dir === 'up') {
      arrow.html('▲');
    } else {
      arrow.html('▼');
    }
  }

  function checkDropdownLocation(trigger) {
    var triggerHeight = trigger.height();
    var menuHeight = trigger.find('.actionMenuContent').height();
    var viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    var menuPositionTop = trigger.offset().top - window.pageYOffset;

    if (menuPositionTop + menuHeight + triggerHeight > viewportHeight) {
      trigger.addClass('to-top');
      setArrow(trigger, 'up');
    } else {
      trigger.removeClass('to-top');
      setArrow(trigger);
    }
  }

  $(global).on('scroll', function() {
    global.requestAnimationFrame(function() {
      $('.actionMenu').each(function(i, e) {
        checkDropdownLocation($(e));
      });
    });
  });

  global.toggleMenuHandler = function toggleMenuHandler(event) {
    event.preventDefault();
    var trigger = $(this).parents('.actionMenu:first');
    checkDropdownLocation(trigger);
    origToggleMenuHandler.call(this);
  };

  global.actionMenuMouseOver = function actionMenuMouseOver() {
    var trigger = $(this).parents('.actionMenu:first');
    checkDropdownLocation(trigger);
    origActionMenuMouseOver.call(this);
  };

  global.hideAllMenus = function hideAllMenus() {
    var menus = $('dl.actionMenu');
    menus.removeClass('to-top');
    origHideAllMenus();
  };
}(
  window,
  window.jQuery,
  window.toggleMenuHandler,
  window.actionMenuMouseOver,
  window.hideAllMenus
));
