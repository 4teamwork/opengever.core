from ftw.testbrowser import browser


def participants():
    return [{'fullname': participant.css('.fullname').first.text,
             'email': participant.css('.email').first.text,
             'present': 'present' in participant.css('.presence').first.classes,
             'role': participant.css('div.role').first.text}
            for participant in browser.css('.participant-list .participant')]
