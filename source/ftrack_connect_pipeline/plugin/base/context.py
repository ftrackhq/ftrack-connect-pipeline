# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.plugin import BasePlugin, BasePluginValidation
from ftrack_connect_pipeline.constants import plugin


class ContextPluginValidation(BasePluginValidation):
    '''
    Context Plugin Validation class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePluginValidation`
    '''

    def __init__(self, plugin_name, required_output, return_type, return_value):
        super(ContextPluginValidation, self).__init__(
            plugin_name, required_output, return_type, return_value
        )

class BaseContextPlugin(BasePlugin):
    '''
    Base Context Plugin Class inherits from
    :class:`~ftrack_connect_pipeline.plugin.BasePlugin`
    '''
    return_type = dict
    '''Required return type'''
    plugin_type = plugin._PLUGIN_CONTEXT_TYPE
    '''Type of the plugin'''
    _required_output = {}
    '''Required return output'''

    def __init__(self, session):
        super(BaseContextPlugin, self).__init__(session)
        self.validator = ContextPluginValidation(
            self.plugin_name, self._required_output, self.return_type,
            self.return_value
        )

    def run(self, context=None, data=None, options=None):
        raise NotImplementedError('Missing run method.')
