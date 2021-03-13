__title__ = "laser cut box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "12/31/20"

__Comment__ = "This module creates a sketch of a laser cut box which can then be saved to an SVG file."

import numpy as np

from enum import Enum

from common import DotDict, BoxType

# Indexes for geoid
START = 1
END = 2
ORIGIN = -1

# Indexes for box sides
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3


# Directional enums for drawing edges
class Direction(Enum):
    EAST = 1
    SOUTH = 2
    WEST = 3
    NORTH = 4


# Face enums for drawing edges
class Face(Enum):
    SIDE = 1
    END = 2
    BOTTOM = 3


class Box:
    def __init__(self, props):
        self.props = props
        self._bottom = []
        self._end = []
        self._side = []

        self._init_properties()

    @property
    def bottom(self):
        return self._bottom

    @property
    def end(self):
        return self._end

    @property
    def side(self):
        return self._side

    @property
    def depth(self):
        return self.props.depth

    @property
    def outer_depth(self):
        return self.props.depth + self.props.thickness

    @property
    def height(self):
        return self.props.height

    @property
    def outer_height(self):
        return self.props.outerHeight

    @property
    def width(self):
        return self.props.width

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

        self.props.sideGap = float((self.props.width - self.props.numTabsWidth * self.props.tabWidth) / (self.props.numTabsWidth + 1))
        self.props.endGap = float((self.props.depth - self.props.numTabsDepth * self.props.tabWidth) / (self.props.numTabsDepth + 1))
        self.props.heightGap = float((self.props.height - self.props.numTabsHeight * self.props.tabWidth) / (self.props.numTabsHeight + 1))

        if self.props.box_type == BoxType.All:
            self.props.outerHeight = self.props.height + self.props.lidThickness + self.props.bottomThickness * 2
        elif self.props.box_type == BoxType.SLOTS:
            self.props.outerHeight = self.props.height + self.props.lidThickness + self.props.bottomThickness
        else:
            self.props.outerHeight = self.props.height + self.props.bottomThickness

    def _build_side(self, face, tab_func):
        if face is Face.SIDE:
            outer_width = self.outer_width
        elif face is Face.END:
            outer_width = self.outer_depth
        else:
            outer_width = 0

        outer_height = self.outer_height

        lower_left, upper_left, lower_right, upper_right = self.get_vectors(outer_width, outer_height)

        side = self._side if face is Face.SIDE else self._end

        side.append((upper_left, upper_right))
        side.extend(self.draw_edge_tabs(face, Direction.EAST, True, outer_height, upper_right))

        if self.props.box_type != BoxType.SLOTS:
            side.extend(self.draw_edge_tabs(face, Direction.SOUTH, True, outer_width, lower_right))
        else:
            side.append((lower_right, lower_left))

        side.extend(self.draw_edge_tabs(face, Direction.WEST, False, outer_height, lower_left))

        if self.props.box_type != BoxType.TABS:
            side.extend(tab_func())

    def build_bottom(self):
        self._bottom = []
        width = self.props.width
        depth = self.props.depth

        lower_left, upper_left, lower_right, upper_right = self.get_vectors(width, depth)

        self._bottom.extend(self.draw_edge_tabs(Face.BOTTOM, Direction.WEST, False, depth, lower_left))
        self._bottom.extend(self.draw_edge_tabs(Face.BOTTOM, Direction.NORTH, False, width, upper_left))
        self._bottom.extend(self.draw_edge_tabs(Face.BOTTOM, Direction.EAST, False, depth, upper_right))
        self._bottom.extend(self.draw_edge_tabs(Face.BOTTOM, Direction.SOUTH, False, width, lower_right))

    def build_long_side(self):
        self._side = []
        self._build_side(Face.SIDE, self.draw_side_slots)

    def build_short_side(self):
        self._end = []
        self._build_side(Face.END, self.draw_end_slots)

    def draw_slot(self, width, height, offset):
        lower_left, upper_left, lower_right, upper_right = self.get_vectors(width, height)

        top = (upper_left + offset, upper_right + offset)
        right = (upper_right + offset, lower_right + offset)
        bottom = (lower_right + offset, lower_left + offset)
        left = (lower_left + offset, upper_left + offset)

        return [top, right, bottom, left]

    def _draw_slots(self, num_tabs, gap, start):
        tabs = []
        tab_width = self.props.tabWidth
        bottom_thickness = self.props.bottomThickness

        for idx in range(0, num_tabs):
            tab = self.draw_slot(tab_width, bottom_thickness, start + self.vector((tab_width + gap) * idx, 0))
            tabs.extend(tab)

        return tabs

    def draw_end_slots(self):
        start = self.vector(self.props.endGap, -(self.props.lidThickness + self.props.bottomThickness))
        return self._draw_slots(self.props.numTabsDepth, self.props.endGap, start)

    def draw_side_slots(self):
        start = self.vector(self.props.sideGap, -(self.props.lidThickness + self.props.bottomThickness))
        return self._draw_slots(self.props.numTabsWidth, self.props.sideGap, start)

    def draw_edge_tabs(self, face, direction, is_inset, length, start):
        is_vertical = direction is Direction.EAST or direction is Direction.WEST
        config = DotDict()
        config.tabWidth = self.props.tabWidth

        lines = []

        def add_line(start_point, end_offset):
            end_point = start_point + end_offset
            if abs(end_point[0]) < 0.0001: end_point[0] = 0.0
            if abs(end_point[1]) < 0.0001: end_point[1] = 0.0

            new_line = (start_point, end_point)

            lines.append(new_line)

            return new_line

        if is_vertical:
            if face is Face.BOTTOM:
                config.numTabs = self.props.numTabsDepth
                config.gap = self.props.endGap
            else:
                config.numTabs = self.props.numTabsHeight
                config.gap = self.props.heightGap

            config.thickness = self.props.thickness

            if (is_inset and direction == Direction.EAST) or (not is_inset and direction == Direction.WEST):
                config.thickness = -config.thickness
        else:
            if face is Face.SIDE or face is Face.BOTTOM:
                config.numTabs = self.props.numTabsWidth
                config.gap = self.props.sideGap
            else:
                config.numTabs = self.props.numTabsDepth
                config.gap = self.props.endGap

            if face is Face.BOTTOM:
                config.thickness = self.props.thickness
            else:
                config.thickness = self.props.bottomThickness

            if (is_inset and direction == Direction.NORTH) or (not is_inset and direction == Direction.SOUTH):
                config.thickness = -config.thickness

        config.longOffset = (length - config.numTabs * config.tabWidth - config.gap * (config.numTabs - 1)) / 2.0
        if direction is Direction.EAST or direction is Direction.SOUTH:
            config.longOffset = -config.longOffset
            config.gap = -config.gap
            config.tabWidth = -config.tabWidth

        if is_vertical:
            first_offset = last_offset = self.vector(0, config.longOffset)
            gap_length = self.vector(0, config.gap)
            tab_length = self.vector(0, config.tabWidth)
            thickness_length = self.vector(config.thickness, 0)
        else:
            if face is Face.BOTTOM:
                first_offset = last_offset = self.vector(config.longOffset, 0)
            else:
                offset = self.vector(self.props.thickness / 2.0, 0)
                first_offset = self.vector(config.longOffset, 0) - offset
                last_offset = self.vector(config.longOffset, 0) + offset

            gap_length = self.vector(config.gap, 0)
            tab_length = self.vector(config.tabWidth, 0)
            thickness_length = self.vector(0, config.thickness)

        line = (0, 0)  # something's wrong if this value gets used

        for idx in range(0, int(config.numTabs)):
            if idx == 0:
                line = add_line(start, first_offset)
            else:
                line = add_line(line[1], gap_length)

            line = add_line(line[1], thickness_length)
            line = add_line(line[1], tab_length)
            line = add_line(line[1], -thickness_length)

        add_line(line[1], last_offset)

        return lines

    # Helper methods
    @staticmethod
    def get_vectors(width, height):
        lower_left = Box.vector(0, -height)
        upper_left = Box.vector(0, 0)
        lower_right = Box.vector(width, -height)
        upper_right = Box.vector(width, 0)

        return lower_left, upper_left, lower_right, upper_right

    @staticmethod
    def vector(x, y):
        return np.array([float(x), float(y)])
