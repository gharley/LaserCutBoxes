__title__ = "living hinge box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "1/21/21"

__Comment__ = "This module creates a living hinge box which can then be saved to an SVG file."

from numpy import pi

from enum import Enum

from common import *

# Indexes for geoid
START = 1
END = 2
CENTER = 3
ORIGIN = -1

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
        self.height = height

        if start_point is None:
            start_point = vector(0, 0)
        self.start_point = start_point

        self.top_line_index = -1
        self.bottom_line_index = -1
        self.offset_line_index = -1

        self._outer_lines = []
        self._inner_lines = []

    @property
    def inner_lines(self):
        return self._inner_lines

    @property
    def outer_lines(self):
        return self._outer_lines

    @property
    def start_point(self):
        return self._start_point

    @start_point.setter
    def start_point(self, value):
        self._start_point = value

    def add_short_lines(self, short_length, gap_length_v, gap_length_h):
        start_point = self.start_point if len(self._outer_lines) == 0 else self._outer_lines[-1][1]

        _, line = add_line(start_point, short_length, self._outer_lines)
        _, line = add_line(line[1], gap_length_v)
        add_line(line[1], short_length, self._outer_lines)

    def draw(self):
        hinge_length = vector(self.length(), 0)
        hinge_height = vector(0, self.height)
        long_length = vector(0, self.height - self.thickness * 2)
        gap_length_v = vector(0, self.thickness * 2)
        gap_length_h = vector(self.segment_width, 0)

        self.bottom_line_index, line = add_line(self.start_point, hinge_length, self._inner_lines)
        self.top_line_index, line = add_line(self.start_point + hinge_height, hinge_length, self._inner_lines)

        for idx in range(0, self.num_segments):
            self.add_short_lines(long_length / 2, gap_length_v, gap_length_h)

            long_start = self._outer_lines[-1][1][1] - (gap_length_h / 2) + (gap_length_v / 2)
            add_line(long_start, long_length, self._inner_lines)

        self.add_short_lines(long_length / 2, gap_length_v, gap_length_h)

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

        self.box_type = BoxType.All
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
        height = props.height
        bottom_thickness = props.bottomThickness
        lid_thickness = props.lidThickness

        props.sideGap = calc_gap(width, props.numTabsWidth, props.tabWidth)

        if self.box_type == BoxType.All:
            actual_height = height + lid_thickness + bottom_thickness * 2.0
        elif self.box_type == BoxType.SLOTS:
            actual_height = height + lid_thickness + bottom_thickness
        else:
            actual_height = height + bottom_thickness

        def draw_lines(top_start, bottom_start, length):
            _, line = add_line(top_start, top_start + length, self._side)
            self._side.append(line)

            if self.box_type == BoxType.SLOTS:
                _, line = add_line(bottom_start, bottom_start + length, self._side)
                self._side.append(line)
            else:
                self._side.append(draw_edge_tabs(Face.SIDE, Direction.NORTH, True, length[0], bottom_start, props))

        def draw_side(top_start, bottom_start, length, num_tabs=1):
            draw_lines(top_start, bottom_start, length)

            # if self.box_type != BoxType.TABS:
            #     draw_slots(num_tabs, length.x, top_start, self.props)

            new_hinge = Hinge(actual_height, bottom_start + length)
            new_hinge.draw()

            top = new_hinge.outer_lines[new_hinge.top_line_index][1]
            bottom = new_hinge.outer_lines[new_hinge.bottom_line_index][1]

            return new_hinge, top, bottom

        lower_left, upper_left, lower_right, upper_right = get_vectors(width, actual_height)

        short_length = vector(depth, 0)
        long_length = vector(width, 0)

        hinge, first_top, first_bottom = draw_side(upper_left, lower_left, short_length / 2.0)
        self._side.append(hinge.outer_lines)
        self._side.append(hinge.inner_lines)

        hinge, hinge_top, hinge_bottom = draw_side(first_top, first_bottom, long_length, props.numTabsWidth)
        hinge, hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, short_length, props.numTabsDepth)
        hinge, hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth)

        draw_lines(hinge_top, hinge_bottom, short_length / 2.0)

        self.draw_dovetails(lower_left, upper_left)
        self.draw_dovetails(hinge_bottom + short_length / 2, hinge_top + short_length / 2.0)

        # if self.box_type != BoxType.TABS:
        #     self.draw_slots(1, short_length.x / 2, hinge_top, self.props)

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
        height = end_point[1] - start_point[1]
        gap = (height - num_tabs * tab_width) / (num_tabs + 1)
        gap_length = vector(0, gap)

        def draw_dovetail(start):
            dt_line = (start, start + vector(tab_width, -tab_width / 2))
            self._side.append(dt_line)
            dt_line = (dt_line[1], dt_line[1] + vector(0, tab_width * 2))
            self._side.append(dt_line)
            dt_line =(dt_line[1], dt_line[1] + vector(-tab_width, -tab_width / 2))
            self._side.append(dt_line)

            return dt_line

        line = (start_point, start_point + gap_length)
        self._side.append(line)

        for idx in range(0, num_tabs):
            line = draw_dovetail(line[1])
            self._side.append(line)
            line = (line[1], line[1] + gap_length)
            self._side.append(line)

    def draw_slots(self, sketch, num_tabs, width, start_point):
        if start_point is None:
            start_point = vector(0, 0)

        tabs = []
        first = []
        tab_width = self.props.tabWidth
        gap = self.props.gapH
        bottom_thickness = self.props.bottomThickness
        offset = (width - num_tabs * self.props.tabWidth - gap * (num_tabs - 1)) / 2
        offset_length = vector(tab_width + gap, 0)
        start_point = start_point + vector(offset, -(self.props.lidThickness + bottom_thickness))

        def draw_slot(start):
            lower_left, upper_left, lower_right, upper_right = get_vectors(tab_width, bottom_thickness)

            top = sketch.addGeometry(Part.LineSegment(upper_left + start, upper_right + start), False)
            right = sketch.addGeometry(Part.LineSegment(lower_right + start, upper_right + start), False)
            bottom = sketch.addGeometry(Part.LineSegment(lower_left + start, lower_right + start), False)
            left = sketch.addGeometry(Part.LineSegment(lower_left + start, upper_left + start), False)

            box = [top, right, bottom, left]

            if self.constrain:
                sketch.addConstraint(Sketcher.Constraint('Horizontal', top))
                sketch.addConstraint(Sketcher.Constraint('Horizontal', bottom))
                sketch.addConstraint(Sketcher.Constraint('Vertical', left))
                sketch.addConstraint(Sketcher.Constraint('Vertical', right))

                sketch.addConstraint(Sketcher.Constraint('Coincident', top, END, right, END))
                sketch.addConstraint(Sketcher.Constraint('Coincident', right, START, bottom, END))
                sketch.addConstraint(Sketcher.Constraint('Coincident', bottom, START, left, START))
                sketch.addConstraint(Sketcher.Constraint('Coincident', left, END, top, START))

                sketch.addConstraint(Sketcher.Constraint('DistanceY', left, bottom_thickness))
                sketch.addConstraint(Sketcher.Constraint('DistanceX', top, tab_width))

            return box

        for idx in range(0, num_tabs):
            tab = draw_slot(start_point + offset_length * idx)
            tabs.append(tab)

            if idx == 0:
                first = tab
            elif self.constrain:
                sketch.addConstraint(Sketcher.Constraint('DistanceX', first[TOP], END, tab[TOP], START, offset_length.x * idx))
                sketch.addConstraint(Sketcher.Constraint('DistanceY', first[TOP], END, tab[TOP], START, 0))

        return tabs
