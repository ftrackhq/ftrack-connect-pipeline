# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin


class NumericValidatorPlugin(plugin.ValidatorPlugin):
    plugin_name = 'numeric'

    def run(self, session=None, context=None, data=None, options=None):
        output = self.output
        self.logger.info('data: {}'.format(data))
        test = options.get('test')
        value = options.get('value')

        if len(data) != 1:
            output = False
            return output

        if test == '>=':
            output = int(data[0]) >= int(value)
            return output


def register(api_object, **kw):
    plugin = NumericValidatorPlugin(api_object)
    plugin.register()
