from lxml import etree as et


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

        for line in lines:
            et.SubElement(g, 'line', {
                'x1': str(line[0][0]),
                'y1': str(line[0][1]),
                'x2': str(line[1][0]),
                'y2': str(line[1][1])
            })

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
