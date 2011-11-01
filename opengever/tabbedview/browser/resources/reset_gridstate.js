function reset_grid_state() {
  jq.ajax({
    url: '@@tabbed_view/setgridstate',
    cache: false,
    type: "POST",
    data: {
      gridstate: "{}",
      view_name: stateName()
    },
    success: function() {
      location.reload();
    }
  });
}
