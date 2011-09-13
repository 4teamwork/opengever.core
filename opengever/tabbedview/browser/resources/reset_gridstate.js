jq(function(){
    jq('#reset_gridstate').live('click',function(){
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
    });
});


