$(function($) {

  function update_clients() {

    // get the amount of clients
    var amount = parseInt($('#amount_of_clients').val(), 10);
    $('#clients_display').html(amount);

    // delete some client configurations, if we have more configs than
    // configured clients
    $('#clients_config .client_config').slice(amount).remove();

    // append new configs
    while($('#clients_config .client_config').length < amount) {
      var index = $('#clients_config .client_config').length + 1;
      $('#default_client_config_scheme .client_config').clone().appendTo(
        '#clients_config').find('.client_id').html(
          'Client ' + index).end().each(function() {
            update_fields($(this), index);
          });
    }

  }

  function get_current_config() {
    /* returns the config dict of the current selected policy */
    var id = $('[name=policy]').val();
    return $(policy_configs).filter(function() {
      if(this['id'] == id) {
        return true;
      }
      return false;
    })[0];
  }

  function load_client_amount() {
    var config = get_current_config();
    var amount = 1;
    if(config.clients && config.clients.length > 0) {
      amount = config.clients.length;
    }
    $('#clients_config .client_config').remove();
    $('#amount_of_clients').val(amount);

    /* also load ldap users import option */
    if(config && config.import_users) {
      $('[name=import_users:boolean]').attr('checked', true);
    }

    update_clients();

    /* warning when purging enabled */
    $('.policy_warnings li').remove();
    if(config && config.purge_sql) {
      $('<li>SQL will be purged completly!</li>').appendTo(
        $('.policy_warnings'));
    }
  }

  /* set the client_amount on initialize */
  load_client_amount();

  /* load the client amount when selecting policy */
  $('[name=policy]').change(function() {
    load_client_amount();
  });

  function update_fields(client, index) {
    var cid = client.find('input[name=clients.client_id:records]').val();
    var subdoms = $('#use_subdomains').attr('checked');

    var config = get_current_config();
    var client_cfg = null;
    if(index && config.clients && config.clients.length >= index) {
      client_cfg = config.clients[index-1];
    }

    // If development profile, set client active by default
    if(config.id == "opengever.examplecontent:0") {
        client.find('input[name=clients.active:boolean]').attr("checked", "checked");
    } else {
      client.find('input[name=clients.active:boolean]').attr('checked', client_cfg.active);
    }

    // If development profile, set default local roles by default
    if(config.id == "opengever.examplecontent:0") {
        client.find('input[name=clients.local_roles:boolean]').attr("checked", "checked");
    } else {
      client.find('input[name=clients.local_roles:boolean]').attr('checked', client_cfg.local_roles);
    }

    if(index) {
      // just created.. need to update
      if(client_cfg && client_cfg.client_id) {
        cid = client_cfg.client_id;
      } else {
        cid = 'mandant'.concat(index);
      }
      client.find('input[name=clients.client_id:records]').val(cid);
      client.find('input[name=clients.index:records]').val(index);
    } else {
      index = client.find('input[name=clients.index:records]').val();
    }

    // title
    if(client_cfg && client_cfg.title) {
      client.find('input[name=clients.title:records]').val(
        client_cfg.title);
    } else {
      client.find('input[name=clients.title:records]').val(
        'Mandant '.concat(index));
    }

    // configure sql
    if(client_cfg && !client_cfg.configsql) {
      client.find('[name=clients.configsql:records]').attr('checked', null);
    }

    // ip address
    if(client_cfg && client_cfg.ip_address) {
      client.find('[name=clients.ip_address:records]').val(
        client_cfg.ip_address);
    } else {
      client.find('[name=clients.ip_address:records]').val('127.0.0.1');
    }

    // internal site URL
    if(client_cfg && client_cfg.site_url) {
      client.find('[name=clients.site_url:records]').val(
        client_cfg.site_url);
    } else {
      client.find('[name=clients.site_url:records]').val(
        'http://localhost:'.concat(
          server_port).concat('/').concat(cid));
    }

    // public site URL
    if(client_cfg && client_cfg.public_url) {
      client.find('[name=clients.public_url:records]').val(
        client_cfg.public_url);

    } else if(location.hostname == 'localhost' && index == 2) {
      client.find('input[name=clients.public_url:records]').val(
        location.protocol.concat('//127.0.0.1:').concat(
          location.port).concat('/').concat(cid));

    } else if(subdoms && location.hostname != 'localhost') {
      client.find('input[name=clients.public_url:records]').val(
        location.protocol.concat('//').concat(cid).concat(
          '.').concat(location.hostname).concat('/'));

    } else {
      client.find('input[name=clients.public_url:records]').val(
        location.protocol.concat('//').concat(
          location.port != '80' ? location.host :
            location.hostname).concat('/').concat(cid));
    }

    // user group
    if(client_cfg && client_cfg.group) {
      client.find('input[name=clients.group:records]').val(
        client_cfg.group);
    } else {
      client.find('input[name=clients.group:records]').val(
        'og_'.concat(cid).concat('_users'));
    }

    // inbox group
    if(client_cfg && client_cfg.inbox_group) {
      client.find('input[name=clients.inbox_group:records]').val(
        client_cfg.inbox_group);
    } else {
      client.find('input[name=clients.inbox_group:records]').val(
        'og_'.concat(cid).concat('_eingangskorb'));
    }

    // reader group
    if(client_cfg && client_cfg.reader_group) {
      client.find('input[name=clients.reader_group:records]').val(
        client_cfg.reader_group);
    } else {
      client.find('input[name=clients.reader_group:records]').val(
        'og_'.concat(cid).concat('_leser'));
    }

    // reader group
    if(client_cfg && client_cfg.rolemanager_group) {
      client.find('input[name=clients.rolemanager_group:records]').val(
        client_cfg.rolemanager_group);
    } else {
      client.find('input[name=clients.rolemanager_group:records]').val(
        'og_'.concat(cid).concat('_rolemanager'));
    }

    // mail domain
    if(client_cfg && client_cfg.mail_domain) {
      client.find('input[name=clients.mail_domain:records]').val(
        client_cfg.mail_domain);

    } else if(location.hostname == 'localhost') {
      client.find('input[name=clients.mail_domain:records]').val(
        'localhost');
    } else {
      client.find('input[name=clients.mail_domain:records]').val(
        cid.concat('.').concat(location.hostname));
    }

    client.find('[name=clients.client_id:records]').change();
  }

  $('#use_subdomains').change(function() {
    $('.client_config').each(function() {
      update_fields($(this), false);
    });
  });

  $('.update_client_id').live('click', function(event) {
    update_fields($(this).parents('.client_config:first'), false);
  });

  if(location.hostname == 'localhost') {
    $('#use_subdomains').attr('disabled', true);
  }

  $('form').submit(function(e) {
    e.preventDefault();

    // disable all inputs
    $('input').attr('disabled', true);
    $('select').attr('disabled', true);

    // defaults
    var ldap = $('[name=ldap]').val();
    var policy = $('[name=policy]').val();
    var import_users = $('[name=import_users:boolean]').attr('checked');

    // hide config fieldset
    $('fieldset.config').hide();

    // submit the clients
    function send_next_client() {
      var client = $('#clients_config .client_config:visible:first');
      if(client.length > 0) {
        var data = {};
        data['ldap'] = ldap;
        data['policy'] = policy;
        client.find('input').each(function() {
          if($(this).attr('name')) {
            var key = $(this).attr('name').split('.')[1].split(':')[0];
            if($(this).attr('type')!='checkbox' ||
               $(this).attr('checked')) {
              data[key] = $(this).val();
            }
          }
        });

        if(data['index'] == 1) {
          data['first'] = '1';
        }

        if(data['index'] == 1 && import_users) {
          data['import_users'] = import_users;
        }

        $('<img src="/++resource++addclient-spinner.gif" class="spinner" />').appendTo(client);

        $.ajax({
          type: 'POST',
          url: '/@@opengever-create-client',
          data: data,
          cache: false,
          success: function(msg) {
            client.hide();
            send_next_client();
          },
          error: function(XMLHttpRequest, textStatus, errorThrown) {
            alert(data['client_id'].concat(': Failed to create client!'));
            client.hide();
            send_next_client();
          }
        });

      } else {

        // after last client
        $('fieldset.clients').hide();
        $('fieldset.complete').show();
        $('fieldset.complete input').attr(
          'disabled', false).click(function() {
            var cid = $('.client_config:first [name=clients.client_id:records]').val();
            window.open(cid, '_self');

          });

      }
    }

    send_next_client();

  });


  /* helpers */

  $('[name=clients.client_id:records]').live('change', function() {
    var dt = $(this).parents('dd:first').prev('dt');
    dt.css('color', null);
    $.ajax({
      url: '/'.concat($(this).val()).concat('/Type'),
      success: function(msg) {
        dt.css('color', 'red');
      }
    });
  });

  $('.import_users_label').click(function(e){
    $(this).parents('.field:first').find('input').click();
    e.preventDefault();
  }).css('cursor', 'default');


  /* initialize */

  $('#clients_config').html('');
  $('#amount_of_clients').bind('click change', function(event) {
    setTimeout(update_clients, 100);
  });
  update_clients();


});
