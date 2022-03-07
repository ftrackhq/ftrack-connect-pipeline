# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.plugin import BasePlugin, BasePluginValidation
from ftrack_connect_pipeline.constants import plugin


class PreFinalizerPluginValidation(BasePluginValidation):
    '''
    Pre Finalizer Plugin Validation class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePluginValidation`
    '''

    def __init__(
        self, plugin_name, required_output, return_type, return_value
    ):
        super(PreFinalizerPluginValidation, self).__init__(
            plugin_name, required_output, return_type, return_value
        )


class BasePreFinalizerPlugin(BasePlugin):
    '''
    Base Pre Finalizer Plugin Class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePlugin`
    '''

    return_type = dict
    '''Required return type'''
    plugin_type = plugin._PLUGIN_PRE_FINALIZER_TYPE
    '''Type of the plugin'''
    _required_output = {}
    '''Required return output'''

    def __init__(self, session):
        super(BasePreFinalizerPlugin, self).__init__(session)
        self.validator = PreFinalizerPluginValidation(
            self.plugin_name,
            self._required_output,
            self.return_type,
            self.return_value,
        )

    def run(self, context_data=None, data=None, options=None):
        raise NotImplementedError('Missing run method.')