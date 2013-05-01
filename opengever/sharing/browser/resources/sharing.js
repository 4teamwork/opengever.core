$(function() {
    var init = function() {
        $('.link-overlay').prepOverlay({
            subtype:'ajax',
            urlmatch:'$',
            urlreplace:''
        });
    };

    /* initalize for sharing view */
    init();

    /* there is also a sharing tab */
    $('.tabbedview_view').bind('reload',
                                init);

});