# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import os
import uuid
import time
import logging
import ftrack_api
from ftrack_connect_pipeline import event
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.definition import collect, validate

logger = logging.getLogger(__name__)


class BaseDefinition(object):
    '''Base Class to represent a Definition'''

    @property
    def session(self):
        '''
        Returns instance of :class:`ftrack_api.session.Session`
        '''
        return self.event_manager.session

    @property
    def event_manager(self):
        '''
        Returns instance of
        :class:`~ftrack_connect_pipeline.event.EventManager`
        '''
        return self._event_manager

    def __init__(self, session):
        '''
        Initialise BasePlugin with instance of
        :class:`ftrack_api.session.Session`
        '''

        self.logger = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )

        self.definition_id = uuid.uuid4().hex

        self._raw_data = []
        self._method = []
        self._event_manager = event.EventManager(
            session=session, mode=constants.LOCAL_EVENT_MODE
        )
        self.__registry = {
            'schema': [],
            'publisher': [],
            'loader': [],
            'opener': [],
            'asset_manager': [],
        }

    def register(self):
        if not isinstance(self.session, ftrack_api.Session):
            # Exit to avoid registering this plugin again.
            return

        self.session.event_hub.subscribe(
            'topic={} and data.pipeline.type=definition'.format(
                constants.PIPELINE_REGISTER_TOPIC
            ),
            self.register_definitions,
        )

    def register_definitions(self, event):
        host_types = event['data']['pipeline']['host_types']
        definition_root_dirs = os.getenv("FTRACK_DEFINITION_PATH").split(os.pathsep)
        for _dir in definition_root_dirs:
            self.logger.debug(
                'Collecting definitions from path: {} '.format(_dir)
            )
            # collect definitions
            _data = collect_and_validate(
                self.session, _dir, host_types
            )
            #TODO: somehow check that are unique items? so can't have duplicated
            # definitions. Think about it.
            for k in list(self.__registry.keys()):
                self.__registry[k].extend(_data[k])
        return self.__registry


def collect_and_validate(session, current_dir, host_types):
    '''
    Collects and validates the definitions and the schemas of the given *host*
    in the given *current_dir*.

    *session* : instance of :class:`ftrack_api.session.Session`
    *current_dir* : Directory path to look for the definitions.
    *host* : Definition host to look for.
    '''
    start = time.time()
    data = collect.collect_definitions(current_dir)

    # # filter definitions
    data = collect.filter_definitions_by_host(data, host_types)
    #
    # # validate schemas
    data = validate.validate_schema(data, session)
    #
    # # resolve schemas

    data = collect.resolve_schemas(data)
    end = time.time()
    logger.info('Discovery run in: {}s'.format(end - start))

    # log final discovery result
    for key, value in list(data.items()):
        logger.debug(
            'Discovering definition took : {} : {}'.format(key, len(value))
        )

    return data
