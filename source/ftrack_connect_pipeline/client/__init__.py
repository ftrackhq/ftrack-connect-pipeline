# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os

import ftrack_api
import logging

from QtExt import QtWidgets

from ftrack_connect_pipeline.client import utils as qtutils
from ftrack_connect_pipeline import event
from ftrack_connect_pipeline.session import get_shared_session
from ftrack_connect_pipeline import constants
from ftrack_connect.ui.widget import header
from ftrack_connect.ui import theme


class BaseQtPipelineWidget(QtWidgets.QWidget):

    @property
    def host(self):
        return self._host

    @property
    def ui(self):
        return self._ui

    def __init__(self, ui, host, parent=None):
        '''Initialise widget with *stage_type* and *stage_mapping*.'''
        super(BaseQtPipelineWidget, self).__init__(parent=parent)

        self._ui = ui
        self._host = host

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.session = get_shared_session()
        self.event_manager = event.EventManager(self.session)

        self.pre_build()
        self.build()
        self.post_build()

        theme.applyFont()

    def resetLayout(self, layout):
        '''Reset layout and delete widgets.'''
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.resetLayout(item.layout())
        # self.stages_manager.reset_stages()
        # self.stages_manager.widgets.clear()


    def pre_build(self):
        '''Build ui method.'''
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.header = header.Header(self.session.api_user)
        self.layout().addWidget(self.header)
        self.combo = QtWidgets.QComboBox()
        self.combo.addItem('- Select asset type -')
        self.layout().addWidget(self.combo)
        self.task_layout = QtWidgets.QVBoxLayout()
        self.layout().addLayout(self.task_layout)
        self.run_button = QtWidgets.QPushButton('Run')
        self.layout().addWidget(self.run_button)

    def build(self):
        pass

    def post_build(self):
        '''Post Build ui method.'''
        self.run_button.clicked.connect(self._on_run)

    def _on_stage_error(self, error):
        self.header.setMessage(error, level='error')

    def _on_stages_end(self):
        self.header.setMessage('DONE!', level='info')

    def _fetch_default_widget(self, plugin, plugin_type):
        plugin_name = 'default.widget'
        plugin_options = plugin.get('options', {})
        name = plugin.get('name', 'no name provided')
        description = plugin.get('description', 'No description provided')

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_REGISTER_TOPIC,
            data={
                'pipeline': {
                    'plugin_name': plugin_name,
                    'plugin_type': plugin_type,
                    'type': 'widget',
                    'ui': self.ui,
                    'host': self.host,
                },
                'settings':
                    {
                        'options': plugin_options,
                        'name': name,
                        'description': description,
                    }
            }
        )

        default_widget = self.session.event_hub.publish(
            event,
            synchronous=True
        )

        return default_widget

    # widget handling
    def fetch_widget(self, plugin, plugin_type):
        '''Fetch widgets defined in the asset schema.'''
        plugin_name = plugin.get('widget', 'default.widget')

        plugin_options = plugin.get('options', {})
        name = plugin.get('name', 'no name provided')
        description = plugin.get('description', 'No description provided')

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_REGISTER_TOPIC,
            data={
                'pipeline': {
                    'plugin_name': plugin_name,
                    'plugin_type': plugin_type,
                    'type': 'widget',
                    'ui': self.ui,
                    'host': self.host,
                },
                'settings':
                    {
                        'options': plugin_options,
                        'name': name,
                        'description': description,
                    }
            }
        )

        result_widget = self.session.event_hub.publish(
            event,
            synchronous=True
        )

        if not result_widget:
            result_widget = self._fetch_default_widget(plugin, plugin_type)

        self.logger.info(result_widget)

        return result_widget[0]

    # Stage management
    def _on_run(self):
        '''Slot triggered with run button.'''
        # start processing the stages.
        # self.stages_manager.reset_stages()
        self.stages_manager.process_stages()