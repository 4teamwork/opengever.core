$(function($) {

    $('#deploy-form').live('submit', function(e) {
        $(this).hide();
        $('#iframe-container').show();
    });

});
