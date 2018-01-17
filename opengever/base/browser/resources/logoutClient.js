(function(global, $) {
  var logoutWorker;

  // Setup the shared worker which holds all open gever tabs
  function initWorker() {
    var workerSrc = global.portal_url + "/++resource++opengever.base/logoutWorker.js";
    logoutWorker = new SharedWorker(workerSrc);
    // Reload the tab when the LogoutBus sends a broadcast message
    logoutWorker.port.onmessage = function() { location.reload(); };
    setupListeners();
  }

  // Prevent the default login behavior. Broadcast a logout message to all open gever tabs instead.
  function trackLogout(e) {
    e.preventDefault();
    e.stopPropagation();
    $.get(global.portal_url + '/logout').done(() => {
      logoutWorker.port.postMessage('logout');
    });
  }

  function setupListeners() {
    var logoutButton = $('#personaltools-logout > a');
    logoutButton.on('click', trackLogout);
  }

  if('SharedWorker' in window) {
    $(initWorker);
  }
})(window, window.jQuery);
