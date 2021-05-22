from PyQt5.QtWidgets import QGraphicsItem, QGraphicsEllipseItem

from common import *


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

    @staticmethod
    def arc_to_qt(arc):
        ellipse = QGraphicsEllipseItem(arc.start, 0, 0, 0)
        pass


class Line(GraphicsItem):
    def __init__(self, start, end):
        super(Line, self).__init__(start, end)
        self._type = 'LINE'


class Arc(GraphicsItem):
    def __init__(self, start, end, radius, start_angle, end_angle):
        super(Arc, self).__init__(start, end)
        self._type = 'ARC'
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
