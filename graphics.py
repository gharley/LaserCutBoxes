from PyQt5.QtWidgets import QGraphicsEllipseItem
import numpy as np


class GraphicsItem:
    def __init__(self, start, end):
        self._type = ''
        self._start = start
        self._end = end

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def type(self):
        return self._type


class Line(GraphicsItem):
    def __init__(self, start, end):
        super(Line, self).__init__(start, end)
        self._type = 'LINE'


class Arc(GraphicsItem):
    def __init__(self, start, end, radius):
        super(Arc, self).__init__(start, end)
        self._type = 'ARC'
        self.radius = radius

    @staticmethod
    def arc_to_qt(arc):
        if arc.start[0] < arc.end[0]:
            if arc.start[1] < arc.end[1]:
                upper_left = arc.start - np.array([0, arc.radius])
                start_angle = 180 * 16
            else:
                upper_left = arc.end - np.array([arc.radius * 2, arc.radius])
                start_angle = 270 * 16
        else:
            if arc.start[1] < arc.end[1]:
                upper_left = arc.start - np.array([arc.radius * 2, -arc.radius])
                start_angle = 0
            else:
                upper_left = arc.start - np.array([arc.radius, 0])
                start_angle = 90 * 16

        ellipse = QGraphicsEllipseItem(upper_left[0], upper_left[1], arc.radius * 2, arc.radius * 2)
        ellipse.setStartAngle(start_angle)
        ellipse.setSpanAngle(90 * 16)

        return ellipse
