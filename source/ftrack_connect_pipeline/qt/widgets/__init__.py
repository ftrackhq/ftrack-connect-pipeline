# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack
import logging
from QtExt import QtWidgets, QtCore


class BaseWidget(QtWidgets.QWidget):

    @property
    def session(self):
        return self._session

    @property
    def data(self):
        return self._data

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @property
    def options(self):
        return self._options

    def __init__(self, parent=None, session=None, data=None, name=None, description=None, options=None):
        super(BaseWidget, self).__init__(parent=parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._session = session
        self._data = data
        self._name = name
        self._description = description
        self._options = options

        self.widget_options = {}

        self.build()

    def build(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        name_label = QtWidgets.QLabel(self.name)
        name_label.setToolTip(self.description)

        layout.addWidget(name_label)
        self.build_options(self.options)

    def extract_options(self):
        raise NotImplementedError()

    def build_options(self, options):
        raise NotImplementedError()
