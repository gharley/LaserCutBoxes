from enum import Enum
import numpy as np

from graphics import Line


# DotDict - easy dictionary access
class DotDict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# Box type enums
class BoxType(Enum):
    All = 0
    SLOTS = 1
    TABS = 2


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


# Line indices
START = 0
END = 1


# Helper methods
def add_line(start_point, end_offset, lines=None):
    end_point = start_point + end_offset
    if abs(end_point[START]) < 0.0001: end_point[START] = 0.0
    if abs(end_point[END]) < 0.0001: end_point[END] = 0.0

    new_line = Line(start_point, end_point)

    if lines is not None:
        lines.append(new_line)
        index = len(lines) - 1
    else:
        index = -1

    return index, new_line


def calc_gap(width, num_tabs, tab_width):
    return float((width - num_tabs * tab_width) / (num_tabs + 1))


def draw_edge_tabs(face, direction, is_inset, length, start, props, num_tabs=None, compensate=True):
    is_vertical = direction is Direction.EAST or direction is Direction.WEST
    config = DotDict()
    config.tabWidth = props.edgeTabWidth if is_vertical and face is not Face.BOTTOM else props.tabWidth

    if is_vertical:
        if face is Face.BOTTOM:
            config.numTabs = props.numTabsDepth
            config.gap = props.endGap
        else:
            config.numTabs = props.numTabsHeight
            config.gap = props.heightGap

        config.thickness = props.thickness

        if (is_inset and direction == Direction.EAST) or (not is_inset and direction == Direction.WEST):
            config.thickness = -config.thickness
    else:
        if face is Face.SIDE or face is Face.BOTTOM:
            config.numTabs = props.numTabsWidth
            config.gap = props.sideGap
        else:
            config.numTabs = props.numTabsDepth
            config.gap = props.endGap

        if face is Face.BOTTOM:
            config.thickness = props.thickness
        else:
            config.thickness = props.bottomThickness

        if (is_inset and direction == Direction.NORTH) or (not is_inset and direction == Direction.SOUTH):
            config.thickness = -config.thickness

    if num_tabs is not None: config.numTabs = num_tabs
    config.longOffset = (length - config.numTabs * config.tabWidth - config.gap * (config.numTabs - 1)) / 2.0

    if direction is Direction.EAST or direction is Direction.SOUTH:
        config.longOffset = -config.longOffset
        config.gap = -config.gap
        config.tabWidth = -config.tabWidth

    if is_vertical:
        first_offset = last_offset = vector(0, config.longOffset)
        gap_length = vector(0, config.gap)
        tab_length = vector(0, config.tabWidth)
        thickness_length = vector(config.thickness, 0)
    else:
        if face is Face.BOTTOM or not compensate:
            first_offset = last_offset = vector(config.longOffset, 0)
        else:
            offset = vector(props.thickness / 2.0, 0)
            first_offset = vector(config.longOffset, 0) - offset
            last_offset = vector(config.longOffset, 0) + offset

        gap_length = vector(config.gap, 0)
        tab_length = vector(config.tabWidth, 0)
        thickness_length = vector(0, config.thickness)

    lines = []
    line = Line(0, 0)

    for idx in range(0, int(config.numTabs)):
        if idx == 0:
            _, line = add_line(start, first_offset, lines)
        else:
            _, line = add_line(line.end, gap_length, lines)

        _, line = add_line(line.end, thickness_length, lines)
        _, line = add_line(line.end, tab_length, lines)
        _, line = add_line(line.end, -thickness_length, lines)

    add_line(line.end, last_offset, lines)

    return lines


def draw_slot(width, height, offset):
    lower_left, upper_left, lower_right, upper_right = get_vectors(width, height)

    top = Line(upper_left + offset, upper_right + offset)
    right = Line(upper_right + offset, lower_right + offset)
    bottom = Line(lower_right + offset, lower_left + offset)
    left = Line(lower_left + offset, upper_left + offset)

    return [top, right, bottom, left]


def draw_slots(num_tabs, gap, start, props):
    tabs = []
    tab_width = props.tabWidth
    bottom_thickness = props.bottomThickness

    for idx in range(0, num_tabs):
        tab = draw_slot(tab_width, bottom_thickness, start + vector((tab_width + gap) * idx, 0))
        tabs.extend(tab)

    return tabs


def get_calculated_properties(props):
    if props.depth == 0:
        props.depth = props.width

    if props.bottomThickness == 0:
        props.bottomThickness = props.thickness

    if props.lidThickness == 0:
        props.lidThickness = props.thickness

    if props.numTabsDepth == 0:
        props.numTabsDepth = props.numTabsWidth

    if props.edgeTabWidth == 0:
        props.edgeTabWidth = props.tabWidth

    props.heightGap = calc_gap(props.height, props.numTabsHeight, props.edgeTabWidth)

    if props.box_type == BoxType.All:
        props.outerHeight = props.height + props.lidThickness + props.bottomThickness * 2
    elif props.box_type == BoxType.SLOTS:
        props.outerHeight = props.height + props.lidThickness + props.bottomThickness
    else:
        props.outerHeight = props.height + props.bottomThickness

    props.gapH = float(
        (props.width - props.radius * 2.0 - props.numTabsWidth * props.tabWidth) / (props.numTabsWidth + 1))
    props.gapV = float(
        (props.depth - props.radius * 2.0 - props.numTabsDepth * props.tabWidth) / (props.numTabsDepth + 1))

    return props


def get_vectors(width, height):
    lower_left = vector(0, -height)
    upper_left = vector(0, 0)
    lower_right = vector(width, -height)
    upper_right = vector(width, 0)

    return lower_left, upper_left, lower_right, upper_right


def vector(x, y):
    return np.array([float(x), float(y)])
