#! /usr/bin/env python
# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import sys

deps_paths = os.environ.get('PYTHONPATH', '').split(os.pathsep)
for path in deps_paths:
    sys.path.append(path)


from qtpy import QtWidgets
from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline import session
from ftrack_connect_pipeline.event import EventManager
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.client import BaseQtPipelineWidget


class QtPipelineLoaderWidget(BaseQtPipelineWidget):
    '''
    Base load widget class.
    '''
    def __init__(self, event_manager, parent=None):

        super(QtPipelineLoaderWidget, self).__init__(event_manager, parent=parent)
        self.setWindowTitle('Standalone Pipeline Loader')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    event_manager = EventManager(
        session=session.get_shared_session(),
        remote=utils.remote_event_mode(),
        ui=constants.UI,
        host=constants.HOST
    )
    wid = QtPipelineLoaderWidget(event_manager)
    wid.show()
    sys.exit(app.exec_())
