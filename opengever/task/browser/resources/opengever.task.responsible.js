jq(window).load(function() {
    /* When the responsible client is updated we need to extend the autocomplete
       search URL of the responsible widget with the client ID. We also do this
       intially. */

    /* for add / edit task and add / edit reponse: */
    $('#form-widgets-responsible_client').change(function(event) {
        var url = $('#form-widgets-responsible-widgets-query')
                .autocomplete('option', 'source').split('?')[0]
                .concat('?client=')
                .concat($(this).find('option:selected').attr('value'));
        $('#form-widgets-responsible-widgets-query')
                .autocomplete('option', 'source', url);
    }).change();
    $('#form-widgets-responsible_client').change(function(event) {
        $('#form-widgets-responsible-input-fields')
                .find('span').remove();
    });

    /* for creating a successor task: */
    $('#form-widgets-client').change(function(event) {
        var url = $('#form-widgets-dossier-widgets-query')
                .autocomplete('option', 'source').split('?')[0]
                .concat('?client=')
                .concat($(this).find('option:selected').attr('value'));
        $('#form-widgets-dossier-widgets-query')
                .autocomplete('option', 'source', url);
    }).change();
    $('#form-widgets-client').change(function(event) {
        $('#form-widgets-dossier-input-fields')
                .find('span').remove();
    });

});
