#! /usr/bin/env python
# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import sys
from collections import OrderedDict

from QtExt import QtWidgets, QtGui, QtCore

from ftrack_connect_pipeline import utils
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.qt import BaseQtPipelineWidget


class QtPipelinePublishWidget(BaseQtPipelineWidget):

    def __init__(self, parent=None):
        stage_type = constants.PUBLISH
        stages_mapping = OrderedDict([
            (constants.CONTEXT,    (constants.CONTEXT_PLUGIN_TOPIC, self.run_context)),
            (constants.COLLECTORS, (constants.COLLECTORS_PLUGIN_TOPIC, self.run_collectors)),
            (constants.VALIDATORS, (constants.VALIDATORS_PLUGIN_TOPIC, self.run_validators)),
            (constants.EXTRACTORS, (constants.EXTRACTORS_PLUGIN_TOPIC, self.run_extractors)),
            (constants.PUBLISHERS, (constants.PUBLISHERS_PLUGIN_TOPIC, self.run_publishers))
        ])
        super(QtPipelinePublishWidget, self).__init__(stage_type, stages_mapping, parent=parent)
        self.setWindowTitle('Standalone Pipeline Publisher')

    def run_context(self):
        '''Run context stage'''
        widgets = self.stages_manager.widgets[self.stages_manager.current_stage]
        event_list = []
        for widget in widgets:
            options = widget.extract_options()
            topic = widget.plugin_topic

            event_list.append(
                {
                    'topic': topic,
                    'options': options,
                    'type': constants.CONTEXT
                }
            )

        self.stages_manager.run_async(event_list)

    def run_collectors(self):
        '''Run collectors stage'''
        widgets = self.stages_manager.widgets[self.stages_manager.current_stage]

        event_list = []

        for widget in widgets:
            options = widget.extract_options()
            topic = widget.plugin_topic

            event_list.append(
                {
                    'topic': topic,
                    'options': options,
                    'type': constants.COLLECTORS
                }
            )

        self.stages_manager.run_async(event_list)

    def run_validators(self):
        '''Run validators stage'''
        widgets = self.stages_manager.widgets[self.stages_manager.current_stage]

        collected_data = utils.merge_list(self.stages_manager.results[constants.COLLECTORS])
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])

        self.logger.debug('collected data:{}'.format(collected_data))
        self.logger.debug('context data:{}'.format(context_data))

        event_list = []

        # TODO: validate context data

        for widget in widgets:
            options = widget.extract_options()
            topic = widget.plugin_topic
            options.update(context_data)
            event_list.append(
                {
                    'topic': topic,
                    'options': options,
                    'data': collected_data,
                    'type': constants.VALIDATORS
                }
            )
        self.stages_manager.run_async(event_list)

    def run_extractors(self):
        '''Run extractors stage'''
        widgets = self.stages_manager.widgets[self.stages_manager.current_stage]

        collected_data = utils.merge_list(self.stages_manager.results[constants.COLLECTORS])
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])
        validators_data = self.stages_manager.results[constants.VALIDATORS]

        if not all(validators_data):
            return

        event_list = []

        # TODO: validate context data

        for widget in widgets:
            options = widget.extract_options()
            topic = widget.plugin_topic
            options.update(context_data)
            event_list.append(
                {
                    'topic': topic,
                    'options': options,
                    'data': collected_data,
                    'type': constants.EXTRACTORS
                }
            )
        self.stages_manager.run_async(event_list)

    def run_publishers(self):
        '''Run validators stage'''
        widgets = self.stages_manager.widgets[self.stages_manager.current_stage]

        extracted_data = self.stages_manager.results[constants.EXTRACTORS]
        context_data = utils.merge_dict(self.stages_manager.results[constants.CONTEXT])
        context_data['asset_type'] = self.asset_type

        validators_data = self.stages_manager.results[constants.VALIDATORS]
        if not all(validators_data):
            return

        event_list = []

        # TODO: validate context data

        for widget in widgets:
            options = widget.extract_options()
            topic = widget.plugin_topic
            options.update(context_data)
            event_list.append(
                {
                    'topic': topic,
                    'options': options,
                    'data': extracted_data,
                    'type': constants.PUBLISHERS
                }
            )
        self.stages_manager.run_async(event_list)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wid = QtPipelinePublishWidget()
    wid.show()
    sys.exit(app.exec_())
