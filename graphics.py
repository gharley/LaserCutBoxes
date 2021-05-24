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
        self.control_point = np.array([self.end[0], self.start[1]])

        if self.start[0] < self.end[0]:
            if self.start[1] < self.end[1]:
                self.upper_left = self.start - np.array([0, self.radius])
                self.control_point = np.array([self.start[0], self.end[1]])
                self.start_angle = 180 * 16
                self.color = QColor(0xff0000)
            else:
                self.upper_left = self.end - np.array([self.radius * 2, self.radius])
                self.control_point = np.array([self.end[0], self.start[1]])
                self.start_angle = 270 * 16
                self.color = QColor(0x00ff00)
        else:
            if self.start[1] < self.end[1]:
                self.upper_left = self.start - np.array([self.radius * 2, -self.radius])
                self.control_point = np.array([self.start[0], self.end[1]])
                self.start_angle = 0
                self.color = QColor(0x0000ff)
            else:
                self.upper_left = self.start - np.array([self.radius, 0])
                # self.control_point = self.end + np.array([self.radius, 0])
                self.start_angle = 90 * 16
                self.color = QColor(0)

    class ArcItem(QGraphicsEllipseItem):
        def __init__(self, x, y, width, height, parent=None):
            super(Arc.ArcItem, self).__init__(x, y, width, height, parent)

        def paint(self, painter: QPainter, option, widget=None) -> None:
            pen = QPen(self.color)
            # pen = QPen(QColor(0))
            pen.setWidth(0)
            painter.setPen(pen)
            painter.drawArc(self.rect(), self.startAngle(), 90 * 16)

    @staticmethod
    def arc_to_qt(arc):
        item = Arc.ArcItem(arc.upper_left[0], arc.upper_left[1], arc.radius * 2, arc.radius * 2)
        item.color = arc.color
        item.setStartAngle(arc.start_angle)

        return item
