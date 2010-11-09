jq(function(){

    // initalize
    if(jq('input[name=form.widgets.portal_type:list]:checked').length == 0){
        jq('input[name=form.widgets.portal_type:list]:first').click();
    }

    // add manually the class for some fields, where the addClass function not work (autocomplete widget ect.)
    jq('#form-widgets-responsible-autocomplete').addClass('opengever-dossier-businesscasedossier');
    jq('#form-widgets-review_state-from').addClass('opengever-dossier-businesscasedossier');
    jq('#form-widgets-creator-autocomplete').addClass('opengever-document-document');
    jq('#form-widgets-checked_out-autocomplete').addClass('opengever-document-document');
    jq('#form-widgets-trashed-0').addClass('opengever-document-document');
    jq('#form-widgets-issuer-autocomplete').addClass('opengever-task-task');
    jq('#form-widgets-task_responsible-autocomplete').addClass('opengever-task-task');

    jq('input[name=form.widgets.portal_type:list]').change(function(){
        var types = ['opengever-dossier-businesscasedossier', 'opengever-task-task', 'opengever-document-document'];
        selected = jq('input[name=form.widgets.portal_type:list]:checked').attr('value').replace(/\./g, '-');
        types.remove(selected);
        // show current
        jq('.'+selected).each(function(){
            jq(this).parents('.field:first').show();
        });
        
        //hide others
        jq(types).each(function(){
            jq('.'+this).each(function(){
                jq(this).parents('.field:first').hide();
            });
        });
    }).change();
    
});
