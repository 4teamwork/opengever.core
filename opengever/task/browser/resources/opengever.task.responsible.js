jq(window).load(function() {
    $('#form-widgets-responsible_client').change(function(event) {
        /* When the responsible client is updated we need to extend the autocomplete
           search URL of the responsible widget with the client ID. We also do this
           intially. */
        $('#form-widgets-responsible-widgets-query').autocomplete(
            'option', 'source',
            $(document).context.URL.concat(
                '/++widget++responsible/@@autocomplete-search?client='.concat(
                    $(this).find('option:selected').attr('value'))));
    }).change();
});
