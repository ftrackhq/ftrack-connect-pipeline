# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import os
import logging
import ftrack_api
import ftrack_api.exception
import tempfile
import uuid

from ftrack_api.cache import FileCache
from ftrack_api.cache import SerialisedCache

_shared_session = None
_shared_file_cache = None

logger = logging.getLogger(
    __name__
)


def get_shared_file_cache(session):
    global _shared_file_cache

    if not _shared_file_cache:
        file_cache_path = os.path.join(tempfile.gettempdir(), '{}.dbm'.format(uuid.uuid4().hex))

        _shared_file_cache = SerialisedCache(
            FileCache(path=file_cache_path),
            encode=session.encode,
            decode=session.decode
        )
        logger.info('creating file cache : {} at {}'.format(_shared_file_cache, file_cache_path))

    else:
        logger.debug('re using file cache: {}'.format(_shared_file_cache))

    return _shared_file_cache


def get_session(plugin_paths=None):

    session = ftrack_api.Session(
        auto_connect_event_hub=False,
        plugin_paths=plugin_paths,
        cache=get_shared_file_cache
    )

    # If is not already connected, connect to event hub.
    if not session.event_hub.connected:
        logger.info('connecting to event hub')
        session.event_hub.connect()
    else:
        logger.debug('already connected to the hub')

    return session


def get_shared_session(plugin_paths=None):
    '''Return shared ftrack_api session.'''
    global _shared_session

    if not _shared_session:
        # Create API session using credentials as stored by the application
        # when logging in.
        _shared_session = get_session(plugin_paths=plugin_paths)
        logger.info('creating new session {}'.format(_shared_session))
    else:
        logger.debug('re using session')

    return _shared_session
