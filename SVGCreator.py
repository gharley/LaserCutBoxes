from lxml import etree as et
import numpy as np

from graphics import Line, Arc


class SVGCreator:
    def __init__(self):
        self._svg = None

    @property
    def svg(self):
        return et.tostring(self._svg)

    def _create_boiler_plate(self, width, height):
        self._svg = et.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'width': '{0}mm'.format(width),
            'height': '{0}mm'.format(height),
            'version': '1.1',
            'style': 'shape-rendering:geometricPrecision',
            'viewBox': '0 0 {0} {1}'.format(width, height)
        })

    def _create_body(self, lines):
        g = et.SubElement(self._svg, 'g', {
            'id': 'boxPart',
            'style': 'stroke:black;stroke-width:0;stroke-linejoin:miter;stroke-miterlimit:2.61313;fill:none;',
            'transform': 'scale(1, -1)'
        })

        et.SubElement(g, 'metadata', {'id': 'Laser cut box by Greg Harley'})
        paths = []
        path_data = []
        arc_mask = 'q {0} {1} {2} {3} '
        line_mask = 'L {0} {1} '
        move_mask = 'M {0} {1} '

        for idx in range(0, len(lines)):
            line = lines[idx]
            if idx > 0:
                prev_line = lines[idx - 1]
                if not (np.isclose(prev_line.end[0], line.start[0]) and np.isclose(prev_line.end[1], line.start[1])):
                    paths.append(''.join(path_data))
                    path_data = []

            if len(path_data) == 0:
                path_data.append(move_mask.format(line.start[0], line.start[1]))

            if isinstance(line, Line):
                path_data.append(line_mask.format(line.end[0], line.end[1]))
            elif isinstance(line, Arc):
                path_data.append(arc_mask.format(line.control_point[0], line.control_point[1], line.length[0], line.length[1]))

        if len(path_data) > 0:
            paths.append(''.join(path_data))

        for path in paths:
            et.SubElement(g, 'path', {'d': path})

    def create_svg(self, width, height, lines):
        self._create_boiler_plate(width, height)
        self._create_body(lines)
        return self.svg

    DOCTYPE = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'

    def write_file(self, filename):
        et.ElementTree(self._svg).write(
            filename,
            encoding='utf-8',
            xml_declaration=True,
            doctype=self.DOCTYPE,
            pretty_print=True
        )
