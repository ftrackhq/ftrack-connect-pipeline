import abc

from QtExt import QtGui, QtCore, QtWidgets


class BaseField(QtWidgets.QWidget):
    '''Base widget to inherit from.'''

    #: Signal to emit on value change.
    value_changed = QtCore.Signal(object)

    @abc.abstractmethod
    def value():
        '''Return value.'''