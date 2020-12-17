# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.plugin import BasePlugin, BasePluginValidation
from ftrack_connect_pipeline.constants import plugin


class OutputPluginValidation(BasePluginValidation):
    '''
    Output Plugin Validation class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePluginValidation`
    '''

    def __init__(self, plugin_name, required_output, return_type, return_value):
        super(OutputPluginValidation, self).__init__(
            plugin_name, required_output, return_type, return_value
        )


class BaseOutputPlugin(BasePlugin):
    '''
    Base Output Plugin Class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePlugin`
    '''
    return_type = dict
    '''Required return type'''
    plugin_type = plugin._PLUGIN_OUTPUT_TYPE
    '''Type of the plugin'''
    _required_output = {}
    '''Required return output'''

    def __init__(self, session):
        super(BaseOutputPlugin, self).__init__(session)
        self.validator = OutputPluginValidation(
            self.plugin_name, self._required_output, self.return_type,
            self.return_value
        )

    def run(self, context=None, data=None, options=None):
        raise NotImplementedError('Missing run method.')