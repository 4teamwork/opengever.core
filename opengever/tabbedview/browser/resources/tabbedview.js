jq(function() {
  arbeitsraum.view_container.bind('reload', function() {
    jq('a.rollover-breadcrumb').tooltip({
      showURL: false,
      track: true,
      fade: 250
    });
  });
});