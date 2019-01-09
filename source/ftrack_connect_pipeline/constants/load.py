from ftrack_connect_pipeline.constants import CONTEXT, _BASE_

LOAD = 'load'
# load stages
COMPONENTS = 'components'
IMPORTERS = 'importers'

# load stack
LOAD_ORDER = [
    CONTEXT,
    COMPONENTS,
    IMPORTERS
]

# load events
COMPONENTS_PLUGIN_TOPIC = '{}.{}.{{}}'.format(_BASE_, COMPONENTS)
INTEGRATORS_PLUGIN_TOPIC = '{}.{}.{{}}'.format(_BASE_, IMPORTERS)

