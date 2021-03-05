from lxml import etree as et


class SVGCreator:
    def __init__(self, width, height, lines):
        self._svg = None
        self._create_boiler_plate(width, height)
        self._create_body(lines)

    @property
    def svg(self):
        return self._svg

    CDATA = '''
        .str0 {stroke:black;stroke-width:7.62;stroke-linejoin:bevel;stroke-miterlimit:2.61313} 
        .fil0 {fill:none}
    '''

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
        g = et.SubElement(self.svg, 'g', {
            'id': 'boxPart',
            'style': 'stroke:black;stroke-width:7.62;stroke-linejoin:miter;stroke-miterlimit:2.61313;fill:none;'})

        et.SubElement(g, 'metadata', {'id': 'Laser cut box by Greg Harley'})

        for line in lines:
            y1 = '{0}'.format(int(line[0][1] * 100))
            y2 = '{0}'.format(int(line[1][1] * 100))

            # If exporting for laser cutting invert the y-axis
            if for_export:
                y1 = '-' + y1
                y2 = '-' + y2

            et.SubElement(g, 'line', {
                'class': '.str0 .fil0',
                'x1': '{0}'.format(int(line[0][0] * 100)),
                'y1': y1,
                'x2': '{0}'.format(int(line[1][0] * 100)),
                'y2': y2,
            })

    DOCTYPE = '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">'

    def write_file(self, filename):
        et.ElementTree(self._svg).write(
            filename,
            encoding='utf-8',
            xml_declaration=True,
            doctype=self.DOCTYPE,
            pretty_print=True
        )
