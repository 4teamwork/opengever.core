jq(window).load(function() {
    /* When the responsible client is updated we need to extend the autocomplete
       search URL of the responsible widget with the client ID. We also do this
       intially. */

    /* if responsble_client is hidden, use the hidden value as source. */
    $('#form-widgets-responsible_client-0').each(function(){
        var url = $('#form-widgets-responsible-widgets-query').
            autocomplete('option', 'source').split('?')[0].
            concat('?client=').
            concat($(this).attr('value'));
        $('#form-widgets-responsible-widgets-query').
            autocomplete('option', 'source', url);
        console.log('updated');
    });

    /* for add / edit task and add / edit reponse: */
    $('#form-widgets-responsible_client').change(function(event) {
        var url = $('#form-widgets-responsible-widgets-query').
            autocomplete('option', 'source').split('?')[0].
            concat('?client=').
            concat($(this).find('option:selected').attr('value'));
        $('#form-widgets-responsible-widgets-query').
            autocomplete('option', 'source', url);
    }).change();
    $('#form-widgets-responsible_client').change(function(event) {
        $('#form-widgets-responsible-input-fields').
            find('span').remove();
    });

    /* for creating a successor task: */
    $('#form-widgets-client').change(function(event) {
        var url = $('#form-widgets-dossier-widgets-query').autocomplete('option', 'source').split('?')[0].concat('?client=').concat($(this).find('option:selected').attr('value'));
        $('#form-widgets-dossier-widgets-query').
            autocomplete('option', 'source', url);
    }).change();
    $('#form-widgets-client').change(function(event) {
        $('#form-widgets-dossier-input-fields').
            find('span').remove();
    });

    /* for copy documents to a remote client */
    $('#formfield-form-widgets-client').change(function(event){
        var url = $('#form-widgets-target_dossier-widgets-query').
            autocomplete('option', 'source').split('?')[0].
            concat('?client=').
            concat($(this).find('.hidden-widget').attr('value'));
        $('#form-widgets-target_dossier-widgets-query').autocomplete('option', 'source', url);
    }).change();

    /* for create dossier in accept-task wizard */
    $('.template-accept_dossier_add_form').each(function() {
        var query = $('#form-widgets-IDossier-responsible-widgets-query');

        var dossier_type = $(this).find('input[name=dossier_type]').
          attr('value');

        console.log(query);
        var url = query.autocomplete('option', 'source').split('?')[0].
          concat('?dossier_type=').concat(dossier_type);
        query.autocomplete('option', 'source', url);
    });

});
