# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging

import ftrack_api
import ftrack_api.exception


_shared_session = None

logger = logging.getLogger(
    __name__
)


def get_shared_session(plugin_paths=None):
    '''Return shared ftrack_api session.'''
    global _shared_session

    if not _shared_session:
        # Create API session using credentials as stored by the application
        # when logging in.
        _shared_session = ftrack_api.Session(
            auto_connect_event_hub=False,
            plugin_paths=plugin_paths
        )
        logger.info('creating new session {}'.format(_shared_session))

    # If is not already connected, connect to event hub.
    if not _shared_session.event_hub.connected:
        logger.info('connecting to event hub')
        _shared_session.event_hub.connect()

    return _shared_session
