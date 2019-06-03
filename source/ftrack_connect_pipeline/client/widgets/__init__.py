# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack



import logging
from qtpy import QtWidgets, QtCore, QtGui

from ftrack_connect_pipeline import constants


class BaseWidget(QtWidgets.QWidget):
    status_updated = QtCore.Signal(object)

    @property
    def status_icons(self):
        '''return the status icons'''
        return self._status_icons

    @property
    def session(self):
        '''return current session object.'''
        return self._session

    @property
    def data(self):
        '''return the widget's data.'''
        return self._data

    @property
    def name(self):
        '''return the widget's name.'''
        return self._name

    @property
    def description(self):
        '''return the widget's description.'''
        return self._description

    @property
    def options(self):
        '''return the widget's options.'''
        return self._options

    def set_option_result(self, value, key):
        '''set the result options of value for the key.'''
        self._results[key] = value

    def get_option_results(self):
        '''return the current option results'''
        return self._results

    def _set_internal_status(self, message_and_satus):
        status = message_and_satus[0]
        message = message_and_satus[1]
        icon = self.status_icons[status]
        self._status_icon.setPixmap(icon)

    def set_status(self, status, message):
        self.status_updated.emit((status, message))

    def _setup_status_icons(self):

        # UNKNOWN
        unknown_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_TitleBarContextHelpButton
        ).pixmap(QtCore.QSize(16, 16))

        # RUNNING
        running_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_BrowserReload
        ).pixmap(QtCore.QSize(16, 16))

        # SUCCESS
        success_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogApplyButton
        ).pixmap(QtCore.QSize(16, 16))

        # ERROR
        error_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_BrowserStop
        ).pixmap(QtCore.QSize(16, 16))

        # EXCEPTION
        exception_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_MessageBoxCritical
        ).pixmap(QtCore.QSize(16, 16))

        # WARNING
        warning_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_MessageBoxWarning
        ).pixmap(QtCore.QSize(16, 16))

        # DEFAULT
        default_icon = self.style().standardIcon(
            QtWidgets.QStyle.SP_MediaPause
        ).pixmap(QtCore.QSize(16, 16))

        self._status_icons = {
            constants.UNKNOWN_STATUS:unknown_icon,
            constants.DEFAULT_STATUS: default_icon,
            constants.ERROR_STATUS: error_icon,
            constants.WARNING_STATUS: warning_icon,
            constants.EXCEPTION_STATUS: exception_icon,
            constants.RUNNING_STATUS: running_icon,
            constants.SUCCESS_STATUS: success_icon,
        }

    def __init__(self, parent=None, session=None, data=None, name=None, description=None, options=None):
        '''initialise widget.'''
        super(BaseWidget, self).__init__(parent=parent)
        self.setParent(parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self._widgets = {}

        self._session = session
        self._data = data
        self._name = name
        self._description = description
        self._options = options
        self._results = {}

        self._setup_status_icons()
        # Build widget
        self.pre_build()
        self.build()
        self.post_build()

    def pre_build(self):
        '''pre build function, mostly used setup the widget's layout.'''
        layout = QtWidgets.QVBoxLayout()

        self._status_icon = QtWidgets.QLabel()
        icon = self.status_icons[constants.DEFAULT_STATUS]
        self._status_icon.setPixmap(icon)
        self._status_icon.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layout.addWidget(self._status_icon)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def build(self):
        '''build function , mostly used to create the widgets.'''
        name_label = QtWidgets.QLabel(self.name)
        name_label.setToolTip(self.description)
        self.layout().addWidget(name_label)

    def post_build(self):
        '''post build function , mostly used connect widgets events.'''
        self.status_updated.connect(self._set_internal_status)
