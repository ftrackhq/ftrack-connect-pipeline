# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
from ftrack_connect_pipeline import plugin


class FilesystemCollectPlugin(plugin.CollectorPlugin):
    plugin_name = 'filesystem'

    def run(self, session=None, context=None, data=None, options=None):
        output = self.output
        output.append(options['path'])
        return output


def register(api_object, **kw):
    plugin = FilesystemCollectPlugin(api_object)
    plugin.register()