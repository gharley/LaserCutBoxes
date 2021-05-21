__title__ = "living hinge box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "1/21/21"

__Comment__ = "This module creates a living hinge box which can then be saved to an SVG file."

from numpy import pi

from enum import Enum

from common import *

# Indexes for box sides
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3


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
            add_line(first_line[END] + gap_length_v, long_length / 2, self._lines)
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
    def side(self):
        return self._side

    @property
    def outer_height(self):
        return self.props.outerHeight

    @property
    def outer_width(self):
        return self.props.width + self.props.thickness

    def _init_properties(self):
        if self.props.depth == 0:
            self.props.depth = self.props.width

        if self.props.bottomThickness == 0:
            self.props.bottomThickness = self.props.thickness

        if self.props.lidThickness == 0:
            self.props.lidThickness = self.props.thickness

        if self.props.numTabsDepth == 0:
            self.props.numTabsDepth = self.props.numTabsWidth

        if self.props.box_type == BoxType.All:
            self.props.outerHeight = self.props.height + self.props.lidThickness + self.props.bottomThickness * 2
        elif self.props.box_type == BoxType.SLOTS:
            self.props.outerHeight = self.props.height + self.props.lidThickness + self.props.bottomThickness
        else:
            self.props.outerHeight = self.props.height + self.props.bottomThickness

        self.props.gapH = float(
            (self.props.width - self.props.radius * 2.0 - self.props.numTabsWidth * self.props.tabWidth) / (self.props.numTabsWidth + 1))
        self.props.gapV = float(
            (self.props.depth - self.props.radius * 2.0 - self.props.numTabsDepth * self.props.tabWidth) / (self.props.numTabsDepth + 1))

        Hinge.radius = self.props.radius
        Hinge.thickness = self.props.thickness
        Hinge.num_segments = self.props.numSegments
        Hinge.segment_width = self.props.segmentWidth

        self.props.adjust = (Hinge.radius * 2 - Hinge.arc_length()) + Hinge.length()

    def build_long_side(self):
        props = self.props

        width = float(props.width - props.adjust)
        depth = float(props.depth - props.adjust)
        props.sideGap = calc_gap(width, props.numTabsWidth, props.tabWidth)

        def draw_lines(top_start, bottom_start, length):
            add_line(top_start, length, self._side)

            if self.props.box_type == BoxType.SLOTS:
                add_line(bottom_start, length, self._side)
            # else:
            #     self._side.extend(draw_edge_tabs(Face.SIDE, Direction.SOUTH, True, length[0], bottom_start, props))

        def draw_side(top_start, bottom_start, length, num_tabs=1):
            draw_lines(top_start, bottom_start, length)

            if self.props.box_type != BoxType.TABS:
                self._side.extend(draw_slots(num_tabs, self.props.gapH, top_start + vector(self.props.gapH, -self.props.bottomThickness), self.props))

            new_hinge = Hinge(self.outer_height, bottom_start + length)
            new_hinge.draw()
            self._side.extend(new_hinge.lines)

            return new_hinge.top_line[END], new_hinge.bottom_line[END]

        lower_left, upper_left, _, _ = get_vectors(width, self.outer_height)

        short_length = vector(depth, 0)
        long_length = vector(width, 0)

        hinge_top, hinge_bottom = draw_side(upper_left, lower_left, short_length / 2.0)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, short_length, props.numTabsDepth)
        hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth)

        draw_lines(hinge_top, hinge_bottom, short_length / 2.0)

        self.draw_dovetails(lower_left, upper_left)
        self.draw_dovetails(hinge_bottom + short_length / 2.0, hinge_top + short_length / 2)

        if self.props.box_type != BoxType.TABS:
            self._side.extend(draw_slots(1, self.props.gapH, hinge_top + vector(self.props.gapH, -self.props.bottomThickness), self.props))

    def build_bottom(self):
        props = self.props

        lower_left, upper_left, lower_right, upper_right = get_vectors(props.width, props.depth)

        radius = props.radius
        width = props.width - radius * 2.0
        depth = props.depth - radius * 2.0
        offset_h = vector(radius, 0)
        offset_v = vector(0, radius)
        last_gap = ((props.depth - props.adjust) / 2.0 - props.tabWidth)

        box = [self.draw_edge_tabs(props.numTabsWidth, width, Direction.NORTH, True, upper_left + offset_h, self.props),
               self.draw_edge_tabs(props.numTabsDepth, depth, Direction.EAST, True, lower_right + offset_v, self.props),
               self.draw_edge_tabs(props.numTabsWidth, width, Direction.SOUTH, True, lower_left + offset_h, self.props),
               self.draw_edge_tabs(2, depth, Direction.WEST, True, lower_left + offset_v, last_gap), self.props]

        arc_stop = sketch.Geometry[box[LEFT][0]].StartPoint.y
        arc_start = sketch.Geometry[box[BOTTOM][0]].StartPoint.x
        circle = Part.Circle(vector(arc_start, arc_stop), vector(0, 0, 1), radius)
        bl = sketch.addGeometry(Part.ArcOfCircle(circle, pi, pi * 1.5), False)

        arc_start = sketch.Geometry[box[TOP][0]].StartPoint.x
        arc_stop = sketch.Geometry[box[LEFT][-1]].EndPoint.y
        circle = Part.Circle(vector(arc_start, arc_stop), vector(0, 0, 1), radius)
        tl = sketch.addGeometry(Part.ArcOfCircle(circle, pi / 2.0, pi), False)

        arc_start = sketch.Geometry[box[TOP][-1]].EndPoint.x
        arc_stop = sketch.Geometry[box[RIGHT][-1]].EndPoint.y
        circle = Part.Circle(vector(arc_start, arc_stop), vector(0, 0, 1), radius)
        tr = sketch.addGeometry(Part.ArcOfCircle(circle, 0, pi / 2.0), False)

        arc_start = sketch.Geometry[box[BOTTOM][-1]].EndPoint.x
        arc_stop = sketch.Geometry[box[RIGHT][0]].StartPoint.y
        circle = Part.Circle(vector(arc_start, arc_stop), vector(0, 0, 1), radius)
        br = sketch.addGeometry(Part.ArcOfCircle(circle, pi * 1.5, 0), False)

    def draw_dovetails(self, start_point, end_point):
        num_tabs = self.props.numTabsHeight
        tab_width = self.props.tabWidth
        height = end_point[END] - start_point[END]
        gap = (height - num_tabs * tab_width) / (num_tabs + 1)
        gap_length = vector(0, gap)

        def draw_dovetail(start):
            _, dt_line = add_line(start, vector(tab_width, -tab_width / 2), self._side)
            _, dt_line = add_line(dt_line[END], vector(0, tab_width * 2), self._side)
            _, dt_line = add_line(dt_line[END], vector(-tab_width, -tab_width / 2), self._side)

            return dt_line

        _, line = add_line(start_point, gap_length, self._side)

        for idx in range(0, num_tabs):
            line = draw_dovetail(line[END])
            _, line = add_line(line[END], gap_length, self._side)
