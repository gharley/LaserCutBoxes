__title__ = "living hinge box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "1/21/21"

__Comment__ = "This module creates a living hinge box which can then be saved to an SVG file."

from numpy import pi

from graphics import Line, Arc
from common import *


class Hinge:
    num_segments = 6
    radius = 15
    segment_width = 3
    thickness = 3

    def __init__(self, height, start_point=None):
        if start_point is None:
            start_point = vector(0, 0)
        self.start_point = start_point

        self.height = height
        self._top_line_index = -1
        self._bottom_line_index = -1
        self._lines = []

    @property
    def bottom_line(self):
        return self._lines[self._bottom_line_index]

    @property
    def lines(self):
        return self._lines

    @property
    def start_point(self):
        return self._start_point

    @start_point.setter
    def start_point(self, value):
        self._start_point = value

    @property
    def top_line(self):
        return self._lines[self._top_line_index]

    def draw(self):
        hinge_length = vector(self.length(), 0)
        hinge_height = vector(0, self.height)
        long_length = vector(0, self.height - self.thickness * 2)
        gap_length_v = vector(0, self.thickness * 2)
        gap_length_h = vector(self.segment_width, 0)
        short_line_start = self.start_point
        long_line_start = self.start_point + gap_length_h / 2 + gap_length_v / 2

        self._top_line_index, line = add_line(self.start_point + hinge_height, hinge_length, self._lines)
        self._bottom_line_index, line = add_line(self.start_point, hinge_length, self._lines)

        def add_short_lines():
            _, first_line = add_line(short_line_start, long_length / 2, self._lines)
            add_line(first_line.end + gap_length_v, long_length / 2, self._lines)
            return short_line_start + gap_length_h

        for idx in range(0, self.num_segments):
            short_line_start = add_short_lines()
            add_line(long_line_start + gap_length_h * idx, long_length, self._lines)

        add_short_lines()

    @staticmethod
    def arc_length():
        return Hinge.radius * 2.0 * pi / 4.0

    @staticmethod
    def length():
        return float(Hinge.segment_width * Hinge.num_segments)


class HingeBox:
    def __init__(self, props):
        self.props = props
        self._bottom = []
        self._side = []

        self._init_properties()

    @property
    def bottom(self):
        return self._bottom

    @property
    def display_depth(self):
        return self.outer_depth

    @property
    def display_height(self):
        return self.outer_height

    @property
    def display_width(self):
        return self.outer_width

    @property
    def display_width_hinge(self):
        return self.outer_width * 2 + self.outer_depth * 2 - Hinge.length() * 4

    @property
    def side(self):
        return self._side

    @property
    def outer_depth(self):
        return self.props.depth + self.props.thickness

    @property
    def outer_height(self):
        return self.props.outerHeight

    @property
    def outer_width(self):
        return self.props.width + self.props.thickness

    def _init_properties(self):
        self.props = get_calculated_properties(self.props)

        Hinge.radius = self.props.radius
        Hinge.thickness = self.props.thickness
        Hinge.num_segments = self.props.numSegments
        Hinge.segment_width = self.props.segmentWidth

        self.props.adjust = (Hinge.radius * 2 - Hinge.arc_length()) + Hinge.length()

        self.props.sideGap = calc_gap(self.props.width - self.props.adjust, self.props.numTabsWidth, self.props.tabWidth)
        self.props.endGap = calc_gap(self.props.depth - self.props.adjust, self.props.numTabsDepth, self.props.tabWidth)

    def build_side(self):
        props = self.props

        # width = float(props.width - Hinge.length())
        # depth = float(props.depth - Hinge.length())
        width = float(props.width - props.adjust)
        depth = float(props.depth - props.adjust)

        def draw_lines(top_start, bottom_start, length, num_tabs):
            add_line(top_start, length, self._side)

            if self.props.box_type == BoxType.SLOTS:
                add_line(bottom_start, length, self._side)
            else:
                self._side.extend(draw_edge_tabs(Face.SIDE, Direction.SOUTH, True, length[0], bottom_start + length, props, num_tabs, False))

        def draw_side(top_start, bottom_start, length, num_tabs=1):
            draw_lines(top_start, bottom_start, length, num_tabs)

            if self.props.box_type != BoxType.TABS:
                self._side.extend(draw_slots(num_tabs, props.gapH, top_start + vector(props.sideGap, -props.bottomThickness), props))

            new_hinge = Hinge(self.outer_height, bottom_start + length)
            new_hinge.draw()
            self._side.extend(new_hinge.lines)

            return new_hinge.top_line.end, new_hinge.bottom_line.end

        lower_left, upper_left, _, _ = get_vectors(width, self.outer_height)

        short_length = vector(depth, 0)
        long_length = vector(width, 0)

        hinge_top, hinge_bottom = draw_side(upper_left, lower_left, short_length / 2.0)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, short_length, props.numTabsDepth)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth)

        draw_lines(hinge_top, hinge_bottom, short_length / 2.0, 1)

        self.draw_dovetails(lower_left, upper_left)
        self.draw_dovetails(hinge_bottom + short_length / 2.0, hinge_top + short_length / 2)

        if props.box_type != BoxType.TABS:
            self._side.extend(draw_slots(1, props.gapH, hinge_top + vector(props.sideGap, -props.bottomThickness), props))

    def build_bottom(self):
        props = self.props

        lower_left, upper_left, lower_right, upper_right = get_vectors(props.width, props.depth)

        radius = props.radius
        width = props.width - radius * 2.0
        depth = props.depth - radius * 2.0
        offset_h = vector(radius, 0)
        offset_v = vector(0, radius)
        last_gap = ((props.depth - props.adjust) / 2.0 - props.tabWidth)

        self._bottom = []
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.NORTH, False, width, upper_left + offset_h, props))
        self._bottom.append(Arc(upper_right - offset_h, upper_right - offset_v, radius))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.EAST, False, depth, upper_right - offset_v, props))
        self._bottom.append(Arc(lower_right + offset_v, lower_right - offset_h, radius))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.SOUTH, False, width, lower_right - offset_h, props))
        self._bottom.append(Arc(lower_left + offset_h, lower_left + offset_v, radius))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.WEST, False, depth, lower_left + offset_v, props, 2))
        self._bottom.append(Arc(upper_left - offset_v, upper_left + offset_h, radius))

    def draw_dovetails(self, start_point, end_point):
        num_tabs = self.props.numTabsHeight
        tab_width = self.props.tabWidth
        height = end_point[1] - start_point[1]
        gap = (height - num_tabs * tab_width) / (num_tabs + 1)
        gap_length = vector(0, gap)

        def draw_dovetail(start):
            _, dt_line = add_line(start, vector(tab_width, -tab_width / 2), self._side)
            _, dt_line = add_line(dt_line.end, vector(0, tab_width * 2), self._side)
            _, dt_line = add_line(dt_line.end, vector(-tab_width, -tab_width / 2), self._side)

            return dt_line

        _, line = add_line(start_point, gap_length, self._side)

        for idx in range(0, num_tabs):
            line = draw_dovetail(line.end)
            _, line = add_line(line.end, gap_length, self._side)
