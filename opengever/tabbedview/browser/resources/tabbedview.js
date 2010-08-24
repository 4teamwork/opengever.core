jq(function() {
  jq('.tabbedview_view').bind('reload', function() {
    /* update breadcrumb tooltips */
    jq('a.rollover-breadcrumb').tooltip({
      showURL: false,
      track: true,
      fade: 250
    });
    /* actions (<a>) should submit the form */
    jq('.buttons a.listing-button').click(function(event) {
      event.preventDefault();
      jq(this).parents('form').append(jq(document.createElement('input')).attr({
        'type' : 'hidden',
        'name' : jq(this).attr('href'),
        'value' : '1'
      })).submit();
    /* make menu */
    });
    jq('ul.buttons').superfish();
  });
});