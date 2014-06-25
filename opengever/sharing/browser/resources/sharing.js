$(function() {
    var init = function() {
        $('.link-overlay').prepOverlay({
            subtype:'ajax',
            urlmatch:'$',
            urlreplace:''
        });
        $('.link-overlay').live('click', function(event) {
            if ($(this).hasClass('overlayed')) return;
            event.preventDefault();
            $(this).prepOverlay({
                subtype:'ajax',
                urlmatch:'$',
                urlreplace:''
            });
            $(this).addClass('overlayed');
            $(this).trigger('click');
        });
    };


    /* initalize for sharing view */
    init();

    /* there is also a sharing tab */
    $('.tabbedview_view').bind('reload',
                                init);

});
