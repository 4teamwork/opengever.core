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
      $.ajaxSetup ({
          // Disable caching of AJAX responses
          cache: false
      });

      /* Workaround: If we just activate the prepOverlay on the link,
      the event onBeforeLoad won't trigger. So we need to add a live-event on the
      link at first. If we click on the logout link, the overlay is preparing.
      To get the overlay, we have to click the button again programmatically.
      */
      $('[href*="logout_overlay"]').live('click', function(e){
          e.preventDefault();

          var overlay = $('[href*="logout_overlay"]').prepOverlay({
              subtype:'ajax',
              formselector:'form[name="logout_overlay"]',
              config: {
                onBeforeLoad : function (e) {
                      var $html = $(e.target).find('.pb-ajax > div').html();
                      if ($html.search('empty:') >= 0){
                          /* The user has no checked out documents. So
                          we can logout him directly.
                          */
                          var $url = $html.replace('empty:', '');
                          e.stopPropagation();
                          e.preventDefault();
                          logout($url);
                      }

                      $('.logout_overlay_submit').click(function(e){
                          e.preventDefault();
                          $url = $('.logout_overlay_redirect').val();
                          logout($url);
                      });
                  }
              }
          });
          overlay.click();
      });
  }

  $(document).ready(function(){
    initLogoutOverlay();
  });

})(window, window.jQuery, window.logoutWorker);
