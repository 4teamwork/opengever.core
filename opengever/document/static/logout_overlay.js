function initLogoutOverlay(){
    jq.ajaxSetup ({
        // Disable caching of AJAX responses
        cache: false
    });

    /* Workaround: If we just activate the prepOverlay on the link,
    the event onBeforeLoad won't trigger. So we need to add a live-event on the
    link at first. If we click on the logout link, the overlay is preparing.
    To get the overlay, we have to click the button again programmatically.
    */
    jq('[href*="logout_overlay"]').live('click', function(e){
        e.preventDefault();

        var overlay = jq('[href*="logout_overlay"]').prepOverlay({
            subtype:'ajax',
            formselector:'form[name="logout_overlay"]',
            config: {
                onBeforeLoad : function (e) {

                    $overlay = e.target.getOverlay();
                    $html = $overlay.find('.pb-ajax > div').html();

                    if ($html.search('empty:') >= 0){
                        /* The user has no checked out documents. So
                        we can logout him directly.
                        */
                        $url = $html.replace('empty:', '');
                        window.open($url, target='_self');
                        return false;
                    }

                    jq('input[name=form.submitted]').click(function(e){
                        e.preventDefault();
                        $url = jq('input[name=form.redirect.url]').val();
                        window.open($url, target='_self');
                        return false;
                    });
                    return true;
                }
            }
        });
        overlay.click();
    });
}

$(document).ready(function(){
   initLogoutOverlay();
});
