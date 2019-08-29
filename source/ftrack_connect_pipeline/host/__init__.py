# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import uuid
import functools
from ftrack_connect_pipeline.host.definition import DefintionManager
from ftrack_connect_pipeline.host.runner import PublisherRunner
from ftrack_connect_pipeline import event, constants, utils
import logging

logger = logging.getLogger(__name__)



def provide_host_information(hostid, event):
    '''return the current hostid'''
    logger.debug('providing hostid: {}'.format(hostid))
    context_id = utils.get_current_context()
    return {'hostid': hostid, 'context_id': context_id}


def initialise(event_manager):
    '''Initialize host with *session*, *host* and *ui*, return *hostid*'''

    event_thread = event.NewApiEventHubThread()
    event_thread.start(event_manager.session)

    definition_manager = DefintionManager(event_manager)
    package_results = definition_manager.packages.result()

    PublisherRunner(
        event_manager,
        package_results
    )

    if event_manager.remote:
        logger.debug('initialising host: {}'.format(hostid))

        handle_event = functools.partial(provide_host_information, event_manager.hostid)
        session.event_hub.subscribe(
            'topic={}'.format(
                constants.PIPELINE_DISCOVER_HOST
            ),
            handle_event
        )


