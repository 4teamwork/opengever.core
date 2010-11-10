jq(function() {
    var init = function() {
        jq('.link-overlay').prepOverlay({
            subtype:'ajax',
            urlmatch:'$',
            urlreplace:''
        });
    };

    /* initalize for sharing view */
    init();

    /* there is also a sharing tab */
    jq('.tabbedview_view').bind('reload',
                                init);

});