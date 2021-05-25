from PyQt5.QtGui import QPainter, QPen, QColor
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
        offset_h = np.array([self.radius, 0])
        offset_v = np.array([0, self.radius])

        self.length = self.end - self.start

        if self.start[0] < self.end[0]:
            if self.start[1] < self.end[1]:
                self.lower_left = self.start - offset_v
                self.start_angle = 180 * 16
                self.control_point = offset_v
            else:
                self.lower_left = self.start - offset_h - offset_v * 2
                self.start_angle = 270 * 16
                self.control_point = offset_h
        else:
            if self.start[1] < self.end[1]:
                self.lower_left = self.end - offset_v
                self.start_angle = 90 * 16
                self.control_point = -offset_h
            else:
                self.lower_left = self.end - offset_h
                self.start_angle = 0
                self.control_point = -offset_v

    class ArcItem(QGraphicsEllipseItem):
        def __init__(self, x, y, width, height, parent=None):
            super(Arc.ArcItem, self).__init__(x, y, width, height, parent)

        def paint(self, painter: QPainter, option, widget=None) -> None:
            pen = QPen(QColor(0))
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawArc(self.rect(), self.startAngle(), 90 * 16)

    @staticmethod
    def arc_to_qt(arc):
        item = Arc.ArcItem(arc.lower_left[0], arc.lower_left[1], arc.radius * 2, arc.radius * 2)
        item.setStartAngle(arc.start_angle)

        return item
