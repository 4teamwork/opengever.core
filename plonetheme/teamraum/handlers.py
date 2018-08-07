from pkg_resources import resource_filename
import io
import os.path
import sass


def compile_scss(event):
    scss_filename = resource_filename('plonetheme.teamraum', 'resources/css/gever/gever.scss')
    scss_directory = os.path.dirname(scss_filename)
    css_map_filename = os.path.join(scss_directory, 'gever.css.map')

    css, css_map = sass.compile(filename=scss_filename, source_map_filename=css_map_filename, output_style='compressed')

    css_filename = os.path.join(scss_directory, 'gever.css')
    css_map_filename = os.path.join(scss_directory, 'gever.css.map')

    with io.open(css_filename, 'w', encoding='UTF-8') as f:
        f.write(css)

    with io.open(css_map_filename, 'w', encoding='UTF-8') as f:
        f.write(css_map)
