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
            'viewBox': '0 0 {0} {1}'.format(int(width * 100), int(height * 100))
        })

    def _create_body(self, lines, for_export=False):
        stroke_width = 7.62 if for_export else '20px'

        g = et.SubElement(self._svg, 'g', {
            'id': 'boxPart',
            'style': 'stroke:black;stroke-width:{0};stroke-linejoin:miter;stroke-miterlimit:2.61313;fill:none;'.format(stroke_width)})

        et.SubElement(g, 'metadata', {'id': 'Laser cut box by Greg Harley'})

        for line in lines:
            y1 = '{0}'.format(int(line[0][1] * 100))
            y2 = '{0}'.format(int(line[1][1] * 100))

            # If exporting for laser cutting invert the y-axis
            if for_export:
                y1 = '-' + y1
                y2 = '-' + y2

            et.SubElement(g, 'line', {
                'x1': '{0}'.format(int(line[0][0] * 100)),
                'y1': y1,
                'x2': '{0}'.format(int(line[1][0] * 100)),
                'y2': y2
            })

    def create_svg(self, width, height, lines, for_export=False):
        self._create_boiler_plate(width, height)
        self._create_body(lines, for_export)
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
