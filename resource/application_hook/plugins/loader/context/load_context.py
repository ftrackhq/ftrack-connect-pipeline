# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class EnvContextPlugin(plugin.ContextPlugin):
    plugin_name = 'context.load'

    def run(self, context=None, data=None, options=None):
        return context


def register(api_object, **kw):
    plugin = EnvContextPlugin()
    plugin.register(api_object)
