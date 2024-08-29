import os


COLORS = {
    'red': '#C3375A',
    'yellow': '#EBD21E',
    'green': '#37C35A'
}


def get_color():
    color = os.environ.get('GEVER_COLORIZATION', None)
    return COLORS.get(color, color or None)
