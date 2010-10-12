$(function($) {

    function update_clients() {

        // get the amount of clients
        var amount = parseInt($('#amount_of_clients').val());
        $('#clients_display').html(amount);

        // delete some client configurations, if we have more configs than
        // configured clients
        $('#clients_config .client_config').slice(amount).remove();

        // append new configs
        while($('#clients_config .client_config').length < amount) {
            var index = $('#clients_config .client_config').length + 1;
            $('#default_client_config_scheme .client_config')
                .clone()
                .appendTo('#clients_config')
                .find('.client_id').html('Client ' + index).end()
                .each(function() {
                    update_fields($(this), index);
                });
        }

    }

    function update_fields(client, index) {
        var cid = client.find('input[name=clients.client_id:records]').val();
        var subdoms = $('#use_subdomains').attr('checked');

        if(index) {
            // just created.. need to update
            cid = client.find('input[name=clients.client_id:records]')
                .val('mandant'.concat(index))
                .val();
            client.find('input[name=clients.index:records]').val(index);
        } else {
            index = client.find('input[name=clients.index:records]').val();
        }

        // title
        client.find('input[name=clients.title:records]')
            .val('Mandant '.concat(index));

        // ip address
        client.find('input[name=clients.ip_address:records]')
            .val('127.0.0.1');

        // internal site URL
        client.find('input[name=clients.site_url:records]')
            .val('http://localhost:'
                 .concat(server_port)
                 .concat('/')
                 .concat(cid));

        // public site URL
        if(location.hostname == 'localhost' && index == 2) {
            client.find('input[name=clients.public_url:records]')
                .val(location.protocol
                     .concat('//127.0.0.1:')
                     .concat(location.port)
                     .concat('/')
                     .concat(cid));

        } else if(subdoms && location.hostname != 'localhost') {
            client.find('input[name=clients.public_url:records]')
                .val(location.protocol
                     .concat('//')
                     .concat(cid).concat('.')
                     .concat(location.hostname)
                     .concat('/'));

        } else {
            client.find('input[name=clients.public_url:records]')
                .val(location.protocol
                     .concat('//')
                     .concat(location.port != '80' ? location.host :
                             location.hostname)
                     .concat('/')
                     .concat(cid));
        }

        // user group
        client.find('input[name=clients.group:records]')
            .val('og_'.concat(cid).concat('_users'));

        // inbox group
        client.find('input[name=clients.inbox_group:records]')
            .val('og_'.concat(cid).concat('_inbox'));
    }

    $('#clients_config').html('');
    $('#amount_of_clients')
        .bind('click change', function(event) {
            setTimeout(update_clients, 100);
        });
    update_clients();

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
        var example = $('input[name=developer:boolean]').attr('checked');
        var lang = $('[name=default_language]').val();
        var ldap = $('[name=ldap]').val();

        // hide config fieldset
        $('fieldset.config').hide();

        // submit the clients
        function send_next_client() {
            var client = $('#clients_config .client_config:visible:first')
            if(client.length > 0) {
                var data = {};
                data['example'] = example ? true : false;
                data['lang'] = lang;
                data['ldap'] = ldap;
                client.find('input').each(function() {
                    if($(this).attr('name')) {
                        var key = $(this).attr('name').split('.')[1].split(':')[0];
                        data[key] = $(this).val();
                    }
                });
                console.info(data);

                if(data['index'] == 1) {
                    data['drop_sql_tables'] = true;
                }

                $('<img src="/++resource++addclient-spinner.gif" class="spinner" />')
                    .appendTo(client);

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
                $('fieldset.complete input')
                    .attr('disabled', false)
                    .click(function() {
                        var cid = $('.client_config:first [name=clients.client_id:records]').val();
                        window.open(cid, '_self');

                    });

            }
        };

        send_next_client();


    });

});
