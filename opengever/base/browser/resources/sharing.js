jq(function() {
    jq('.link-overlay').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',
        urlreplace:''
        });
});