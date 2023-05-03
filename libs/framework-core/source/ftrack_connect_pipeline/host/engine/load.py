# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.host.engine import BaseEngine


class LoaderEngine(BaseEngine):
    engine_type = 'loader'

    def __init__(self, event_manager, host_types, host_id, asset_type_name):
        super(LoaderEngine, self).__init__(
            event_manager, host_types, host_id, asset_type_name
        )