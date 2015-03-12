from ftw.testbrowser.widgets.base import widget
from ftw.testbrowser.widgets.datetime import DateTimeWidget


@widget
class OpengeverDateTimeWidget(DateTimeWidget):
    """Customize ftw.testbrowser's DateTimeWidget for Opengever/older Plone
    versions.

    Somehow filling the month field does not work with zero padded month values
    """

    def fill(self, value):
        self._field('day').value = value.strftime('%d')
        self._field('month').value = value.strftime('%m').lstrip('0')
        self._field('year').value = value.strftime('%Y')

        if not self._field('hour'):
            return

        if self._field('ampm'):
            self._field('hour').value = value.strftime('%I')
            self._field('ampm').value = value.strftime('%p')

        else:
            self._field('hour').value = value.strftime('%H')

        minute = self._field('min') or self._field('minute')
        minute.value = value.strftime('%M')
