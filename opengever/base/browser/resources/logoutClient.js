(function(global, $) {
  var logoutWorker;

  // Setup the shared worker which holds all open gever tabs
  function initWorker() {
    var workerSrc = global.portal_url + "/++resource++opengever.base/logoutWorker.js?r=1";
    logoutWorker = new SharedWorker(workerSrc);
    // Reload the tab when the LogoutBus sends a broadcast message
    logoutWorker.port.onmessage = function(e) {
      window.location = e.data[0];
    };
  }

  // Prevent the default login behavior. Broadcast a logout message to all open gever tabs instead.
  function logout(url) {
    // Reject the promise immediately when the logout worker has not been initialized
    if (!logoutWorker) {
      return $.Deferred().reject();
    }

    // Trigger the logout and broadcast to the other gever tabs
    logoutWorker.port.postMessage([url]);
    return $.Deferred().resolve();
  }

  // Check if SharedWorker is supported
  if('SharedWorker' in window) {
    $(initWorker);
  }

  // Pop the logout API to the global scope
  window.logoutWorker = {};
  window.logoutWorker.logout = logout;

})(window, window.jQuery);
