#! /usr/bin/env python
# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import sys
import os

deps_paths = os.environ.get('PYTHONPATH', '').split(os.pathsep)
for path in deps_paths:
    sys.path.append(path)

from collections import OrderedDict

from QtExt import QtGui

from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.qt import BaseQtPipelineWidget


class QtPipelinePublishWidget(BaseQtPipelineWidget):

    def __init__(self, ui, host, parent=None):
        stage_type = constants.PUBLISH
        stages_mapping = OrderedDict([
            (constants.CONTEXT,    self.run_context),
            (constants.COLLECTORS, self.run_collectors),
            (constants.VALIDATORS, self.run_validators),
            (constants.EXTRACTORS, self.run_extractors),
            (constants.PUBLISHERS, self.run_publishers)
        ])
        super(QtPipelinePublishWidget, self).__init__(stage_type, stages_mapping, ui, host, parent=parent)
        self.setWindowTitle('Standalone Pipeline Publisher')

    def run_context(self):
        '''Run context stage'''
        data = self.stages_manager.widgets.get(self.stages_manager.current_stage, [])
        event_list = []
        for (widget, plugin) in data:
            context = widget.extract_options()

            event_list.append(
                {
                    'settings': {
                        'context': context,
                        'data': None,
                        'options': None
                    },
                    'pipeline': {
                        'plugin_name': plugin['plugin'],
                        'plugin_type': self.stages_manager.current_stage,
                        'type': 'plugin',
                        'host': self.host
                    },
                }
            )

        self.stages_manager.run_async(event_list)

    def run_collectors(self):
        '''Run collectors stage'''
        data = self.stages_manager.widgets.get(self.stages_manager.current_stage, [])

        event_list = []
        for (widget, plugin) in data:
            options = widget.extract_options()

            event_list.append(
                {
                    'settings': {
                        'context': None,
                        'data': None,
                        'options': options
                    },
                    'pipeline': {
                        'plugin_name': plugin['plugin'],
                        'plugin_type': self.stages_manager.current_stage,
                        'type': 'plugin',
                        'host': self.host,
                    },
                }
            )

        self.stages_manager.run_async(event_list)

    def run_validators(self):
        '''Run validators stage'''
        data = self.stages_manager.widgets[self.stages_manager.current_stage]

        collected_data = utils.merge_list(self.stages_manager.results[constants.COLLECTORS])
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])

        self.logger.debug('collected data:{}'.format(collected_data))
        self.logger.debug('context data:{}'.format(context_data))

        event_list = []

        for (widget, plugin) in data:
            options = widget.extract_options()

            event_list.append(
                {
                    'settings': {
                        'context': context_data,
                        'data': collected_data,
                        'options': options
                    },
                    'pipeline': {
                        'plugin_name': plugin['plugin'],
                        'plugin_type': self.stages_manager.current_stage,
                        'type': 'plugin',
                        'host': self.host,
                    },
                }
            )

        self.stages_manager.run_async(event_list)

    def run_extractors(self):
        '''Run extractors stage'''
        data = self.stages_manager.widgets[self.stages_manager.current_stage]

        collected_data = utils.merge_list(self.stages_manager.results[constants.COLLECTORS])
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])
        validators_data = self.stages_manager.results[constants.VALIDATORS]

        if not all(validators_data):
            return

        event_list = []

        # TODO: validate context data

        for (widget, plugin) in data:
            options = widget.extract_options()

            event_list.append(
                {
                    'settings': {
                        'context': context_data,
                        'data': collected_data,
                        'options': options
                    },
                    'pipeline': {
                        'plugin_name': plugin['plugin'],
                        'plugin_type': self.stages_manager.current_stage,
                        'type': 'plugin',
                        'host': self.host,
                    },
                }
            )

        self.stages_manager.run_async(event_list)

    def run_publishers(self):
        '''Run validators stage'''
        data = self.stages_manager.widgets[self.stages_manager.current_stage]

        extracted_data = self.stages_manager.results[constants.EXTRACTORS]
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])
        context_data['asset_type'] = self.asset_type

        validators_data = self.stages_manager.results[constants.VALIDATORS]
        if not all(validators_data):
            return

        event_list = []

        # TODO: validate context data

        for (widget, plugin) in data:
            options = widget.extract_options()

            event_list.append(
                {
                    'settings': {
                        'context': context_data,
                        'data': extracted_data,
                        'options': options
                    },
                    'pipeline': {
                        'plugin_name': plugin['plugin'],
                        'plugin_type': constants.PUBLISHERS,
                        'type': 'plugin',
                        'host': self.host,
                    },
                }
            )

        self.stages_manager.run_async(event_list)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wid = QtPipelinePublishWidget(ui=constants.UI, host=constants.HOST)
    wid.show()
    sys.exit(app.exec_())