#!/usr/bin/python

from jinja2 import Environment
from jinja2 import FileSystemLoader
from jinja2 import select_autoescape
import os


def main():
    env = Environment(
        loader=FileSystemLoader("/etc/postfix"),
        autoescape=select_autoescape(),
        trim_blocks=True,
    )

    config = {
        'inet_protocols': 'ipv4',
        'message_size_limit': '31457280',
        'mailbox_size_limit': '52428800',
        'smtp_tls_security_level': 'verify',
        'smtp_tls_ciphers': 'high',
        'smtp_tls_mandatory_ciphers': 'high',
        'smtp_tls_protocols': '>=TLSv1.2',
        'smtp_tls_mandatory_protocols': '>=TLSv1.2',
        'smtpd_tls_security_level': 'may',
    }
    environ = {
        k.lower()[8:]: v
        for k, v in os.environ.items() if k.startswith('POSTFIX_')
    }
    config.update(environ)

    template = env.get_template("main.cf.jinja")
    with open('/etc/postfix/main.cf', 'w') as f:
        f.write(template.render(config=config))

    virtual_domains = []
    for k, v in os.environ.items():
        if k.startswith('VIRTUAL_DOMAINS_'):
            virtual_domain = {}
            for kv_pair in v.split(','):
                name, sep, val = kv_pair.partition('=')
                virtual_domain[name] = val

            if 'name' in virtual_domain and 'url' in virtual_domain:
                virtual_domains.append(virtual_domain)

    template = env.get_template("virtual.jinja")
    with open('/etc/postfix/virtual', 'w') as f:
        f.write(template.render(virtual_domains=virtual_domains))
    template = env.get_template("aliases.jinja")
    with open('/etc/aliases', 'w') as f:
        f.write(template.render(virtual_domains=virtual_domains))
    template = env.get_template("sni.jinja")

    tls_domains = []
    for virtual_domain in virtual_domains:
        if os.path.exists(f'/etc/postfix/sni-chains/{virtual_domain["name"]}.pem'):
            tls_domains.append(virtual_domain)
    with open('/etc/postfix/sni', 'w') as f:
        f.write(template.render(virtual_domains=tls_domains))


if __name__ == '__main__':
    main()
