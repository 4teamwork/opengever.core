jq('[href*=jobs_view]').live('click', function(e){
    e.preventDefault();
    var queue_name = this.textContent;
    tabbedview.param('view_name', 'jobs');
    tabbedview.param('queue', queue_name);
    tabbedview.reload_view();
});


jq(function () {
    jq('#tabbedview-body').prepend('<a href="javascript:tabbedview.reload_view()">Reload</a>');
});