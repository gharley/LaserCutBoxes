__title__ = "living hinge box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "1/21/21"

__Comment__ = "This module creates a living hinge box which can then be saved to an SVG file."

from numpy import pi

from enum import Enum

from common import BoxType, add_line, vector, get_vectors

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


# Directional enums for drawing edges
class Direction(Enum):
    NS = 1
    EW = 2
    SN = 3
    WE = 4


class Hinge:
    num_segments = 6
    radius = 15
    segment_width = 3
    thickness = 3

    def __init__(self, sketch, height, start_point=None, constrain=False):
        self.sketch = sketch
        self.constrain = constrain
        self.height = height

        if start_point is None:
            start_point = vector(0, 0)
        self.start_point = start_point

        self.long_line_index = -1
        self.short_line_index = -1
        self.gap_v_line_index = -1
        self.gap_h_line_index = -1
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
        first_time = self.short_line_index == -1
        start_point = self.start_point if len(self._outer_lines) == 0 else self._outer_lines[-1][1]

        line = add_line(start_point, short_length, self._outer_lines)
        line = add_line(line[1], gap_length_v, self._outer_lines)
        line = add_line(line[1], short_length, self._outer_lines)
        line = add_line(start_point, gap_length_h, self._outer_lines)

    def draw(self):
        hinge_length = vector(self.length(), 0)
        hinge_height = vector(0, self.height)
        long_length = vector(0, self.height - self.thickness * 2)
        gap_length_v = vector(0, self.thickness * 2)
        gap_length_h = vector(self.segment_width, 0)

        self.bottom_line_index = self.sketch.addGeometry(Part.LineSegment(self.start_point, self.start_point + hinge_length), False)

        self.top_line_index = self.sketch.addGeometry(
            Part.LineSegment(self.start_point + hinge_height, self.start_point + hinge_height + hinge_length), False)

        for idx in range(0, self.num_segments):
            self.add_short_lines(long_length / 2, gap_length_v, gap_length_h)

            long_start = self.sketch.Geometry[self._outer_lines[-1]].EndPoint - (gap_length_h / 2) + (gap_length_v / 2)
            line_index, inner_line = add_line(long_start, long_length, self._inner_lines)

            if idx == 0:
                self.long_line_index = line_index

            line_index, inner_line = add_line(long_start, gap_length_h, self._inner_lines, (self._inner_lines[-1], START))
            self.sketch.toggleConstruction(line_index)

        self.add_short_lines(long_length / 2, gap_length_v, gap_length_h)

    @staticmethod
    def arc_length():
        return Hinge.radius * 2.0 * pi / 4.0

    @staticmethod
    def length():
        return float(Hinge.segment_width * Hinge.num_segments)


class Box:
    def __init__(self, props):
        self.props = props
        self.box_type = BoxType.All
        self._init_properties()

    def _init_properties(self):
        if self.props.depth == 0:
            self.props.depth = self.props.width

        if self.props.bottomThickness == 0:
            self.props.bottomThickness = self.props.thickness

        if self.props.lidThickness == 0:
            self.props.lidThickness = self.props.thickness

        if self.props.numTabsDepth == 0:
            self.props.numTabsDepth = self.props.numTabsWidth

        self.props.gapH = float(
            (self.props.width - self.props.radius * 2.0 - self.props.numTabsWidth * self.props.tabWidth) / (self.props.numTabsWidth + 1))
        self.props.gapV = float(
            (self.props.depth - self.props.radius * 2.0 - self.props.numTabsDepth * self.props.tabWidth) / (self.props.numTabsDepth + 1))

        Hinge.radius = self.props.radius
        Hinge.thickness = self.props.thickness
        Hinge.num_segments = self.props.numSegments
        Hinge.segment_width = self.props.segmentWidth

        self.props.adjust = (Hinge.radius * 2 - Hinge.arc_length()) + Hinge.length()

    def build_side(self):
        props = self.props
        sketch = self._add_sketch('BoxSide')

        width = float(props.width - props.adjust)
        depth = float(props.depth - props.adjust)
        height = props.height
        bottom_thickness = props.bottomThickness
        lid_thickness = props.lidThickness

        if self.box_type == BoxType.All:
            actual_height = height + lid_thickness + bottom_thickness * 2.0
        elif self.box_type == BoxType.SLOTS:
            actual_height = height + lid_thickness + bottom_thickness
        else:
            actual_height = height + bottom_thickness

        def draw_lines(top_start, bottom_start, length, num_tabs=1):
            line1 = (top_start, top_start + length)

            if self.box_type == BoxType.SLOTS:
                line2 = [(bottom_start, bottom_start + length)]
            else:
                line2 = self.draw_edge_tabs(num_tabs, length.x, Direction.WE, False, bottom_start)

            return line1, line2

        def draw_side(top_start, bottom_start, length, num_tabs=1, old_hinge=None):
            top_line, bottom_line = draw_lines(top_start, bottom_start, length, num_tabs)

            if self.box_type != BoxType.TABS:
                slots = self.draw_slots(sketch, num_tabs, length.x, top_start)

            new_hinge = Hinge(sketch, actual_height, bottom_start + length)
            new_hinge.draw()

            top = sketch.Geometry[new_hinge.top_line_index].EndPoint
            bottom = sketch.Geometry[new_hinge.bottom_line_index].EndPoint

            return new_hinge, top, bottom

        lower_left, upper_left, lower_right, upper_right = get_vectors(width, actual_height)

        short_length = vector(depth, 0)
        long_length = vector(width, 0)

        hinge, first_top, first_bottom = draw_side(upper_left, lower_left, short_length / 2.0)
        hinge, hinge_top, hinge_bottom = draw_side(first_top, first_bottom, long_length, props.numTabsWidth, hinge)
        hinge, hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, short_length, props.numTabsDepth, hinge)
        hinge, hinge_top, hinge_bottom = draw_side(hinge_top, hinge_bottom, long_length, props.numTabsWidth, hinge)

        last_top, last_bottom = draw_lines(hinge_top, hinge_bottom, short_length / 2.0)

        self.draw_dovetails(sketch, lower_left, upper_left)
        self.draw_dovetails(sketch, hinge_bottom + short_length / 2, hinge_top + short_length / 2.0)

        if self.box_type != BoxType.TABS:
            self.draw_slots(sketch, 1, short_length.x / 2, hinge_top)

    def build_bottom(self):
        props = self.props
        sketch = self._add_sketch('BoxBottom')

        lower_left, upper_left, lower_right, upper_right = get_vectors(props.width, props.depth)

        radius = props.radius
        width = props.width - radius * 2.0
        depth = props.depth - radius * 2.0
        offset_h = vector(radius, 0)
        offset_v = vector(0, radius)
        last_gap = ((props.depth - props.adjust) / 2.0 - props.tabWidth)

        box = [self.draw_edge_tabs(sketch, props.numTabsWidth, width, Direction.WE, True, upper_left + offset_h),
               self.draw_edge_tabs(sketch, props.numTabsDepth, depth, Direction.NS, True, lower_right + offset_v),
               self.draw_edge_tabs(sketch, props.numTabsWidth, width, Direction.EW, True, lower_left + offset_h),
               self.draw_edge_tabs(sketch, 2, depth, Direction.SN, True, lower_left + offset_v, last_gap)]

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

    def draw_dovetails(self, sketch, start_point, end_point):
        num_tabs = self.props.numTabsHeight
        tab_width = self.props.tabWidth
        height = end_point.y - start_point.y
        gap = (height - num_tabs * tab_width) / (num_tabs + 1)
        gap_length = vector(0, gap)

        def draw_dovetail(start):
            dt_line = Part.LineSegment(start, start + vector(tab_width, -tab_width / 2))
            sketch.addGeometry(dt_line, False)
            dt_line = Part.LineSegment(dt_line.EndPoint, dt_line.EndPoint + vector(0, tab_width * 2))
            sketch.addGeometry(dt_line, False)
            dt_line = Part.LineSegment(dt_line.EndPoint, dt_line.EndPoint + vector(-tab_width, -tab_width / 2))
            sketch.addGeometry(dt_line, False)

            return dt_line

        line = Part.LineSegment(start_point, start_point + gap_length)
        sketch.addGeometry(line, False)

        for idx in range(0, num_tabs):
            line = draw_dovetail(line.EndPoint)
            line = Part.LineSegment(line.EndPoint, line.EndPoint + gap_length)
            sketch.addGeometry(line, False)

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

    def draw_edge_tabs(self, sketch, num_tabs, length, direction, is_bottom, start, gap=None):
        props = self.props
        is_vertical = direction is Direction.NS or direction is Direction.SN

        if gap is None:
            gap = props.gapV if is_vertical else props.gapH

        offset = (length - num_tabs * props.tabWidth - gap * (num_tabs - 1)) / 2.0

        lines = []

        def add_line(start_point, end_offset, previous):
            end_point = start_point + end_offset
            new_line = Part.LineSegment(start_point, end_point)
            new_index = sketch.addGeometry(new_line, False)

            if self.constrain and previous != -1:
                sketch.addConstraint(Sketcher.Constraint('Coincident', previous, END, new_index, START))
                sketch.addConstraint(Sketcher.Constraint('Perpendicular', previous, new_index))

            lines.append(new_index)

            return new_index, new_line

        if is_vertical:
            offset_length = vector(0, offset)

            thickness = props.thickness

            if direction == Direction.SN:
                thickness = -thickness

            gap_length = vector(0, gap)
            tab_length = vector(0, props.tabWidth)
            thickness_length = vector(thickness, 0)
        else:
            offset_length = vector(offset, 0)

            if is_bottom:
                thickness = -props.thickness
            else:
                thickness = props.bottomThickness

            if (is_bottom and direction == Direction.WE) or (not is_bottom and direction == Direction.EW):
                thickness = -thickness

            gap_length = vector(gap, 0)
            tab_length = vector(props.tabWidth, 0)
            thickness_length = vector(0, thickness)

        gap_line_index = -1
        first_tab_index = -1
        offset_line_index = -1
        thickness_line_index = -1
        line_index = -1
        line = Optional[Part.LineSegment]

        for idx in range(0, num_tabs):
            if idx == 0:
                line_index, line = add_line(start, offset_length, line_index)

                offset_line_index = line_index
                if self.constrain:
                    if is_vertical:
                        sketch.addConstraint(Sketcher.Constraint('Vertical', offset_line_index))
                    else:
                        sketch.addConstraint(Sketcher.Constraint('Horizontal', offset_line_index))
            else:
                line_index, line = add_line(line.EndPoint, gap_length, line_index)

                if gap_line_index == -1:
                    gap_line_index = line_index
                    if self.constrain:
                        constraint_type = 'DistanceY' if is_vertical else 'DistanceX'
                        sketch.addConstraint(Sketcher.Constraint(constraint_type, gap_line_index, gap))
                elif self.constrain:
                    sketch.addConstraint(Sketcher.Constraint('Equal', gap_line_index, line_index))

            line_index, line = add_line(line.EndPoint, thickness_length, line_index)

            if idx == 0:
                thickness_line_index = line_index
                if self.constrain:
                    constraint_type = 'DistanceX' if is_vertical else 'DistanceY'
                    sketch.addConstraint(Sketcher.Constraint(constraint_type, thickness_line_index, thickness))
            elif self.constrain:
                sketch.addConstraint(Sketcher.Constraint('Equal', thickness_line_index, line_index))

            line_index, line = add_line(line.EndPoint, tab_length, line_index)

            if idx == 0:
                first_tab_index = line_index
                if self.constrain:
                    constraint_type = 'DistanceY' if is_vertical else 'DistanceX'
                    sketch.addConstraint(Sketcher.Constraint(constraint_type, first_tab_index, props.tabWidth))
            elif self.constrain:
                sketch.addConstraint(Sketcher.Constraint('Equal', first_tab_index, line_index))

            line_index, line = add_line(line.EndPoint, -thickness_length, line_index)
            if self.constrain:
                sketch.addConstraint(Sketcher.Constraint('Equal', thickness_line_index, line_index))

        line_index, line = add_line(line.EndPoint, offset_length, line_index)

        if self.constrain:
            index = line_index if direction == Direction.NS or direction == Direction.EW else offset_line_index
            constraint_type = 'DistanceY' if is_vertical else 'DistanceX'
            sketch.addConstraint(Sketcher.Constraint(constraint_type, index, offset))

        return lines

    @staticmethod
    def _add_sketch(sketch_name):
        body = App.ActiveDocument.addObject('PartDesign::Body', sketch_name)
        sketch = App.ActiveDocument.addObject('Sketcher::SketchObject', sketch_name + 'Sketch')
        body.addObject(sketch)

        return sketch

    @staticmethod
    def _constrain_sides(sketch, box):
        sketch.addConstraint(Sketcher.Constraint('Coincident', box[LEFT][0], START, box[TOP][0], START))
        sketch.addConstraint(Sketcher.Constraint('Coincident', box[TOP][-1], END, box[RIGHT][-1], END))
        sketch.addConstraint(Sketcher.Constraint('Coincident', box[RIGHT][-1], END, box[BOTTOM][-1], END))
        sketch.addConstraint(Sketcher.Constraint('Coincident', box[BOTTOM][0], START, box[LEFT][0], START))

    @staticmethod
    def get_line(sketch, index):
        return sketch.Geometry[index]

    @staticmethod
    def get_line_length(sketch, line_array, is_vertical):
        start_line = sketch.Geometry[line_array[0]]
        end_line = sketch.Geometry[line_array[-1]]

        if is_vertical:
            length = end_line.EndPoint.y - start_line.StartPoint.y
        else:
            length = end_line.EndPoint.x - start_line.StartPoint.x

        return length

    @staticmethod
    def log(message):
        App.Console.PrintMessage(str(message) + '\n')


Box()
