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


class Line(GraphicsItem):
    def __init__(self, start, end):
        super(Line, self).__init__(start, end)
        self._type = 'LINE'


class Arc(Line):
    def __init__(self, start, end, radius):
        super(Arc, self).__init__(start, end)
        self._type = 'ARC'
        self.radius = radius
