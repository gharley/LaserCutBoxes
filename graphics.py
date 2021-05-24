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

        if self.start[0] < self.end[0]:
            if self.start[1] < self.end[1]:
                self.upper_left = self.start - np.array([0, self.radius])
                self.control_point = self.end - np.array([self.radius, 0])
                self.start_angle = 180 * 16
            else:
                self.upper_left = self.end - np.array([self.radius * 2, self.radius])
                self.control_point = self.start + np.array([self.radius, 0])
                self.start_angle = 270 * 16
        else:
            if self.start[1] < self.end[1]:
                self.upper_left = self.start - np.array([self.radius * 2, -self.radius])
                self.control_point = self.end + np.array([self.radius, 0])
                self.start_angle = 0
            else:
                self.upper_left = self.start - np.array([self.radius, 0])
                self.control_point = self.start - np.array([0, self.radius])
                self.start_angle = 90 * 16

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
        item = Arc.ArcItem(arc.upper_left[0], arc.upper_left[1], arc.radius * 2, arc.radius * 2)
        item.setStartAngle(arc.start_angle)

        return item
