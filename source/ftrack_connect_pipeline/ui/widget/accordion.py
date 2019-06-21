import logging
from qtpy import QtWidgets, QtCore, QtGui


class AccordionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None, title=None):
        super(AccordionWidget, self).__init__(parent=parent)

        self._is_collasped = True
        self._title_frame = None
        self._content, self._content_layout = (None, None)

        self._main_v_layout = QtWidgets.QVBoxLayout(self)

        title_widget = self.initTitleFrame(title, self._is_collasped)
        self._main_v_layout.addWidget(title_widget)

        content_widget = self.initContent(self._is_collasped)
        self._main_v_layout.addWidget(content_widget)

        self.initCollapsable()

    def initTitleFrame(self, title, collapsed):
        self._title_frame = AccordionTitleWidget(
            title=title, collapsed=collapsed)

        return self._title_frame

    def initContent(self, collapsed):
        self._content = QtWidgets.QWidget()
        self._content_layout = QtWidgets.QVBoxLayout()

        self._content.setLayout(self._content_layout)
        self._content.setVisible(not collapsed)

        return self._content

    def addWidget(self, widget):
        self._content_layout.addWidget(widget)

    def initCollapsable(self):
        self._title_frame.clicked.connect(self.toggleCollapsed)

    def toggleCollapsed(self):
        self._content.setVisible(self._is_collasped)
        self._is_collasped = not self._is_collasped
        self._title_frame._arrow.setArrow(int(self._is_collasped))


class AccordionTitleWidget(QtWidgets.QFrame):
    def __init__(self, parent=None, title="", collapsed=False):
        super(AccordionTitleWidget, self).__init__(parent=parent)

        self.setMinimumHeight(24)
        self.move(QtCore.QPoint(24, 0))
        self.setStyleSheet("border:1px solid rgb(41, 41, 41); ")

        self._hlayout = QtWidgets.QHBoxLayout(self)
        self._hlayout.setContentsMargins(0, 0, 0, 0)
        self._hlayout.setSpacing(0)

        self._arrow = None
        self._title = None

        self._hlayout.addWidget(self.initArrow(collapsed))
        self._hlayout.addWidget(self.initTitle(title))

    def initArrow(self, collapsed):
        self._arrow = Arrow(collapsed=collapsed)
        self._arrow.setStyleSheet("border:0px")

        return self._arrow

    def initTitle(self, title=None):
        self._title = QtWidgets.QLabel(title)
        self._title.setMinimumHeight(24)
        self._title.move(QtCore.QPoint(24, 0))
        self._title.setStyleSheet("border:0px")

        return self._title

    def mousePressEvent(self, event):
        self.clicked.emit()
        # self.emit(QtCore.SIGNAL('clicked()'))

        return super(AccordionTitleWidget, self).mousePressEvent(event)


class Arrow(QtWidgets.QFrame):
    def __init__(self, parent=None, collapsed=False):
        super(Arrow, self).__init__(parent=parent)

        self.setMaximumSize(24, 24)

        # horizontal == 0
        self._arrow_horizontal = QtGui.QPolygonF().fromList(
            [
                QtCore.QPointF(7.0, 8.0),
                QtCore.QPointF(17.0, 8.0),
                QtCore.QPointF(12.0, 13.0)
            ]
        )
        # vertical == 1
        self._arrow_vertical = QtGui.QPolygonF().fromList(
            [
                QtCore.QPointF(8.0, 7.0),
                QtCore.QPointF(13.0, 12.0),
                QtCore.QPointF(8.0, 17.0)
            ]
        )
        # arrow
        self._arrow = None
        self.setArrow(int(collapsed))

    def setArrow(self, arrow_dir):
        if arrow_dir:
            self._arrow = self._arrow_vertical
        else:
            self._arrow = self._arrow_horizontal

    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setBrush(QtGui.QColor(192, 192, 192))
        painter.setPen(QtGui.QColor(64, 64, 64))
        painter.drawPolygon(self._arrow)
        painter.end()
