# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import logging
import ftrack_api
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.host.engine.base_load_publish import BaseLoaderPublisherEngine


class PublisherEngine(BaseLoaderPublisherEngine):
    engine_type = 'publisher'

    def __init__(self, event_manager, host, hostid, asset_type):
        '''Initialise publisherEngine with *event_manager*, *host*, *hostid* and
        *asset_type*'''
        super(PublisherEngine, self).__init__(
            event_manager, host, hostid, asset_type
        )



