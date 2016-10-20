// Red 'required' indicator for fields in schema docs

$(function() {
    $('span.required').parents('.attribute').find('dt > code').addClass('required-marker');
});


// Collapsibles

$(function() {
    $(".collapsible > *").hide();
    $(".collapsible .header").show();
    $(".collapsible .header").click(function() {
        $(this).parent().children().not(".header").toggle();
        $(this).parent().children(".header").toggleClass("open");
    });
});
