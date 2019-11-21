# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import threading
import sys
import logging
import types

import os
from Qt import QtCore, QtWidgets

from ftrack_connect_pipeline import constants

def get_current_context():
    '''return an api object representing the current context.'''
    context_id = os.getenv(
        'FTRACK_CONTEXTID',
            os.getenv('FTRACK_TASKID',
                os.getenv('FTRACK_SHOTID'
            )
        )
    )

    return context_id


def remote_event_mode():
    return bool(os.environ.get(
        constants.PIPELINE_REMOTE_EVENTS_ENV, 0
    ))


class Worker(QtCore.QThread):
    '''Perform work in a background thread.'''

    def __init__(self, function, args=None, kwargs=None, parent=None):
        '''Execute *function* in separate thread.

        *args* should be a list of positional arguments and *kwargs* a
        mapping of keyword arguments to pass to the function on execution.

        Store function call as self.result. If an exception occurs
        store as self.error.

        Example::

            try:
                worker = Worker(theQuestion, [42])
                worker.start()

                while worker.isRunning():
                    app = QtGui.QApplication.instance()
                    app.processEvents()

                if worker.error:
                    raise worker.error[1], None, worker.error[2]

            except Exception as error:
                traceback.print_exc()
                QtGui.QMessageBox.critical(
                    None,
                    'Error',
                    'An unhandled error occurred:'
                    '\\n{0}'.format(error)
                )

        '''
        super(Worker, self).__init__(parent=parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.result = None
        self.error = None

    def run(self):
        '''Execute function and store result.'''
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as error:
            self.logger.error(str(error))
            self.error = sys.exc_info()


def asynchronous(method):
    '''Decorator to make a method asynchronous using its own thread.'''

    def wrapper(*args, **kwargs):
        '''Thread wrapped method.'''

        def exceptHookWrapper(*args, **kwargs):
            '''Wrapp method and pass exceptions to global excepthook.

            This is needed in threads because of
            https://sourceforge.net/tracker/?func=detail&atid=105470&aid=1230540&group_id=5470
            '''
            try:
                method(*args, **kwargs)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                sys.excepthook(*sys.exc_info())

        thread = threading.Thread(
            target=exceptHookWrapper,
            args=args,
            kwargs=kwargs
        )
        thread.start()

    return wrapper


class MainThreadWorker(QtCore.QObject):

    __main_thread_lock = threading.Lock()
    __signal = QtCore.Signal(object)
    _async = False

    def __init__(self, asynchronous=False):
        super(MainThreadWorker, self).__init__()
        self.function = None
        self.result = None
        self._async = asynchronous
        if QtCore.QCoreApplication.instance():
            self.moveToThread(QtCore.QCoreApplication.instance().thread())

    def _check_args_type(self, *args):
        if type(args) != types.TupleType:
            args = (args,)
        return args

    def run(self, function, *args, **kwargs):
        args = self._check_args_type(*args)
        self.function = lambda: function(*args, **kwargs)
        print "function in run ---> {0}".format(self.function)
        if self._async:
            self._async_run()#(self.function, *args, **kwargs)
        else:
            return self._sync_run()#(self.function, *args, **kwargs)

    def _sync_run(self):
        self.__main_thread_lock.acquire()
        try:
            print " before invoke metod "
            QtCore.QMetaObject.invokeMethod(self, "_execute_function", QtCore.Qt.BlockingQueuedConnection)#QtCore.Qt.BlockingQueuedConnection)
            print " after invoke method "
        except Exception, e:
            print " There was an error invoking method ---> {}".format(e)
        finally:
            print " finally releasing thread "
            self.__main_thread_lock.release()

        return self.result

    @QtCore.Slot()
    def _execute_function(self):
        """
        Execute the function
        """
        if self._async:
            self.function()
        else:
            print "function in _execute_function ---> {0}".format(self.function)
            self.result = self.function()

    def _async_run(self):
        self._async=True
        self.__signal.connect(self._execute_function)
        self.__signal.emit(self.function)

    def execute_in_main_thread(self, func, *args, **kwargs):
        #We shoud add if async no return
        if (QtWidgets.QApplication.instance()):
            if (QtCore.QThread.currentThread() != QtWidgets.QApplication.instance().thread()):
                print "yes we are executing in the main thread"
                result = self.run(func, *args, **kwargs)
                print "this is the result {0}".format(result)
                return result  # invoker.invoke(func, *args, **kwargs)
        print "We are are in the main thread"
        return func(*args, **kwargs)


