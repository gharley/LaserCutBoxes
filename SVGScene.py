from threading import Timer

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QPen, QColor, QTransform


class SVGScene(QGraphicsScene):
    def __init__(self, view: QGraphicsView):
        super(SVGScene, self).__init__()

        self.view = view
        view.setScene(self)
        view.installEventFilter(self)

    def add_lines(self, lines):
        self.clear()
        pen = QPen(QColor(0))
        pen.setWidth(0)

        for line in lines:
            self.addLine(line[0][0], -line[0][1], line[1][0], -line[1][1], pen)

        self.scale()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Resize:
            timer = Timer(0.1, self.scale)
            timer.start()

        return False

    def scale(self):
        scene_rect = self.view.sceneRect()
        if scene_rect.height() != 0:
            self.view.setTransform(QTransform())
            view_rect = self.view.rect()
            height_aspect = view_rect.height() / scene_rect.height()
            width_aspect = view_rect.width() / scene_rect.width()
            scale = min(height_aspect, width_aspect) * 0.95  # leave a little margin
            self.view.scale(scale, scale)
