function initCheckoutCancelConfirmation(){

  // submitting
  $('form#cancel_confirmation').live('submit', function(e){
    $(this).parents('.pb-ajax').siblings('.close').click();
    return true
  });

  // cancel
  $('form#cancel_confirmation #cancel').live('click', function(e){
    $(this).parents('.pb-ajax').siblings('.close').click();
  });
}

$(document).ready(function(){
  initCheckoutCancelConfirmation();
});
