# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging

import ftrack_api
import ftrack_api.exception
import threading


logger = logging.getLogger(
    __name__
)


def get_shared_session(plugin_paths=None):
    '''Return shared ftrack_api session.'''

        # Create API session using credentials as stored by the application
        # when logging in.

    my_threading = threading.local()
    if not hasattr(my_threading, '_api_session'):
        my_threading._api_session =  ftrack_api.Session(
        auto_connect_event_hub=False,
        plugin_paths=plugin_paths
    )

    # If is not already connected, connect to event hub.
    if not my_threading._api_session.event_hub.connected:
        logger.debug('connecting to event hub')
        my_threading._api_session.event_hub.connect()

    logger.debug('creating new session {}'.format(my_threading._api_session))

    return my_threading._api_session
