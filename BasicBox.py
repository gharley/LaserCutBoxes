__title__ = "laser cut box"
__author__ = "Greg Harley"
__version__ = "01.00"
__date__ = "12/31/20"

__Comment__ = "This module creates a sketch of a laser cut box which can then be saved to an SVG file."

from common import *

# Indexes for geoid
START = 1
END = 2
ORIGIN = -1

# Indexes for box sides
TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3


class BasicBox:
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

        if self.props.edgeTabWidth == 0:
            self.props.edgeTabWidth = self.props.tabWidth

        self.props.sideGap = calc_gap(self.props.width, self.props.numTabsWidth, self.props.tabWidth)
        self.props.endGap = calc_gap(self.props.depth, self.props.numTabsDepth, self.props.tabWidth)
        self.props.heightGap = calc_gap(self.props.height, self.props.numTabsHeight, self.props.edgeTabWidth)

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

        lower_left, upper_left, lower_right, upper_right = get_vectors(outer_width, outer_height)

        side = self._side if face is Face.SIDE else self._end

        side.append((upper_left, upper_right))
        side.extend(draw_edge_tabs(face, Direction.EAST, True, outer_height, upper_right, self.props))

        if self.props.box_type != BoxType.SLOTS:
            side.extend(draw_edge_tabs(face, Direction.SOUTH, True, outer_width, lower_right, self.props))
        else:
            side.append((lower_right, lower_left))

        side.extend(draw_edge_tabs(face, Direction.WEST, False, outer_height, lower_left, self.props))

        if self.props.box_type != BoxType.TABS:
            side.extend(tab_func())

    def build_bottom(self):
        self._bottom = []
        width = self.props.width
        depth = self.props.depth

        lower_left, upper_left, lower_right, upper_right = get_vectors(width, depth)

        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.WEST, False, depth, lower_left, self.props))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.NORTH, False, width, upper_left, self.props))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.EAST, False, depth, upper_right, self.props))
        self._bottom.extend(draw_edge_tabs(Face.BOTTOM, Direction.SOUTH, False, width, lower_right, self.props))

    def build_long_side(self):
        self._side = []
        self._build_side(Face.SIDE, self.draw_side_slots)

    def build_short_side(self):
        self._end = []
        self._build_side(Face.END, self.draw_end_slots)

    def draw_end_slots(self):
        start = vector(self.props.endGap, -self.props.lidThickness)
        return draw_slots(self.props.numTabsDepth, self.props.endGap, start, self.props)

    def draw_side_slots(self):
        start = vector(self.props.sideGap, -self.props.lidThickness)
        return draw_slots(self.props.numTabsWidth, self.props.sideGap, start, self.props)
