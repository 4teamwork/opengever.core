(function(global, $) {
  var logoutWorker;

  // Setup the shared worker which holds all open gever tabs
  function initWorker() {
    var workerSrc = global.portal_url + "/++resource++opengever.base/logoutWorker.js";
    logoutWorker = new SharedWorker(workerSrc);
    // Reload the tab when the LogoutBus sends a broadcast message
    logoutWorker.port.onmessage = function() { location.reload(); };
  }

  // Prevent the default login behavior. Broadcast a logout message to all open gever tabs instead.
  function logout(url) {
    // Reject the promise immediately when the logout worker has not been initialized
    if (!logoutWorker) {
      return $.Deferred().promise().reject();
    }

    // Trigger the logout and broadcast to the other gever tabs
    return $.get(url).done(function() {
      logoutWorker.port.postMessage('logout');
    });
  }

  // Check if SharedWorker is supported
  if('SharedWorker' in window) {
    $(initWorker);
  }

  // Pop the logout API to the global scope
  window.logoutWorker = {};
  window.logoutWorker.logout = logout;

})(window, window.jQuery);
