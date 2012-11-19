function initDeleteConfirmation(){

  // submitting
  $('form#download_confirmation').live('submit', function(e){
    $(this).parents('.pb-ajax').siblings('.close').click();
    return true
  });

  // cancel
  $('form#download_confirmation #cancel').live('click', function(e){
    $(this).parents('.pb-ajax').siblings('.close').click();
  });
}

$(document).ready(function(){
  initDeleteConfirmation();
});
