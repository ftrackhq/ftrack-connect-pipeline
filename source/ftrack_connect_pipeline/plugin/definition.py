# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack
import json

from ftrack_connect_pipeline import exception
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.plugin import BasePlugin


class BasePackagePlugin(BasePlugin):

    @property
    def discover_topic(self):
        return self._base_topic(constants.PIPELINE_REGISTER_TOPIC)

    @property
    def run_topic(self):
        return self._base_topic(constants.PIPELINE_REGISTER_TOPIC)

    def _base_topic(self, topic):
        required = [
            self.plugin_type,
        ]

        if not all(required):
            raise exception.PluginError('Some required fields are missing')

        topic = 'topic={} and data.pipeline.type={}'.format(
            topic,
            self.plugin_type
        )
        return topic

    def _run(self, event):
        raw_result = self.run()

        result_valid, message = self._validate_result_type(raw_result)
        if not result_valid:
            raise Exception(message)

        return json.dumps(raw_result)

    def run(self):
        raise NotImplementedError()


# PLUGINS
class PackageDefinition(BasePackagePlugin):
    plugin_type = constants.PACKAGE
    return_type = dict


class PublisherDefintion(BasePackagePlugin):
    plugin_type = constants.PUBLISHER
    return_type = dict


class LoaderDefition(BasePackagePlugin):
    plugin_type = constants.LOADER
    return_type = str
