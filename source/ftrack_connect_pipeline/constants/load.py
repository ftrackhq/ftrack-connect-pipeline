from ftrack_connect_pipeline.constants import _BASE_

LOAD = 'load'
# load stages
COMPONENTS = 'components'
IMPORTERS = 'importers'

# load events
COMPONENTS_PLUGIN_TOPIC = '{}.{}.{{}}'.format(_BASE_, COMPONENTS)
IMPORTERS_PLUGIN_TOPIC = '{}.{}.{{}}'.format(_BASE_, IMPORTERS)

