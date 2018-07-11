(function(global, $, logoutWorker) {

  function logout(url) {
      // Trigger the logout on the SharedWorker instance
      logoutWorker.logout(url).fail(function() {
        /*
          Open the url without the SharedWorker when something went wrong.
          This usually happens when SharedWorker is not supported
        */
        window.open(url, '_self');
      });
  }

  function initLogoutOverlay(){
      var url = $('[href*="logout"]').attr('href');

      $('[href*="logout"]').live('click', function(e){
          e.preventDefault();
          logout(url);
      });
  }

  $(document).ready(function(){
    initLogoutOverlay();
  });

})(window, window.jQuery, window.logoutWorker);
