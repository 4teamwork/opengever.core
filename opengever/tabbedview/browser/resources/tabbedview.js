jq(function() {
    jq('.tabbedview_view').bind('reload', function() {
        /* update breadcrumb tooltips */
        jq('a.rollover-breadcrumb').tooltip({
            showURL: false,
            track: true,
            fade: 250
        });

        // make more menu work
        initializeMenus();

        /* actions (<a>) should submit the form */
        jq('#tabbedview-menu a.actionicon').click(function(event) {
            event.preventDefault();
            jq(this).parents('form').append(jq(document.createElement('input')).attr({
                'type' : 'hidden',
                'name' : jq(this).attr('href'),
                'value' : '1'
            })).submit();
        });
    });

    initializeMenus();
});