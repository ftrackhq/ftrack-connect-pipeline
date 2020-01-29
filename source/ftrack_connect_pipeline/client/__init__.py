# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import time
import logging
import copy
import ftrack_api
import python_jsonschema_objects as pjo

from ftrack_connect_pipeline import constants


class HostConnection(object):

    @property
    def definitions(self):
        return self._raw_host_data['definitions']

    @property
    def id(self):
        return self._raw_host_data['host_id']

    @property
    def host_definitions(self):
        return self._raw_host_data['host_id'].split("-")[0].split(".")

    def __repr__(self):
        return '<HostConnection: {}>'.format(self.id)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __init__(self, event_manager, host_data):
        self.logger = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )

        copy_data = copy.deepcopy(host_data)

        self.session = event_manager.session
        self._event_manager = event_manager
        self._raw_host_data = copy_data

        self.on_client_notification()

    def run(self, data):
        '''Send *data* to the host through the given *topic*.'''
        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_HOST_RUN,
            data={
                'pipeline': {
                    'host_id': self.id,
                    'data': data,
                }
            }
        )
        self._event_manager.publish(
            event,
        )

    def _notify_client(self, event):
        '''*event* callback to update widget with the current status/value'''
        data = event['data']['pipeline']['data']
        status = event['data']['pipeline']['status']
        plugin_name = event['data']['pipeline']['plugin_name']
        message = event['data']['pipeline']['message']

        if constants.status_bool_mapping[status]:
            self.logger.info('plugin_name: {} \n status: {} \n result: {} \n '
                             'message: {}'.format(plugin_name, status,
                                                  data, message))

        if status == constants.ERROR_STATUS or \
                status == constants.EXCEPTION_STATUS:
            raise Exception('An error occurred during the execution of the '
                            'plugin name {} \n message: {} \n data: {}'.format(
                plugin_name, message, data))

    def on_client_notification(self):
        self.session.event_hub.subscribe(
            'topic={} and data.pipeline.hostid={}'.format(
                constants.PIPELINE_CLIENT_NOTIFICATION,
                self._raw_host_data['host_id']),
            self._notify_client
        )


class Client(object):
    '''
    Base client widget class.
    '''

    @property
    def connected(self):
        return self._connected

    @property
    def hosts(self):
        '''Return the current ui type.'''
        return self._host_list

    def __init__(self, event_manager, ui=None):
        '''Initialise widget with *ui* , *host* and *hostid*.'''
        self._packages = {}
        self._current = {}
        self.ui = [constants.UI]

        ui = ui or []
        self.ui.extend(ui)
        self.ui = list(set(self.ui))

        self._host_list = []
        self._connected = False

        self.__callback = None
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.event_manager = event_manager
        self.session = event_manager.session

    def discover_hosts(self, time_out=5):
        # discovery host loop and timeout.
        start_time = time.time()
        self.logger.info('time out set to {}:'.format(time_out))
        if not time_out:
            self.logger.warning(
                'Running client with no time out.'
                'Will not stop until discover a host.'
                'Terminate with: Ctrl-C'
            )

        while not self.hosts:
            delta_time = time.time() - start_time

            if time_out and delta_time >= time_out:
                self.logger.warning('Could not discover any host.')
                break

            self._discover_hosts()

        if self.__callback and self.hosts:
            self.__callback(self.hosts)

        return self.hosts

    def _host_discovered(self, event):
        '''callback to to add new hosts *event*.'''
        if not event['data']:
            return
        host_connection = HostConnection(self.event_manager, event['data'])
        if host_connection not in self.hosts:
            self._host_list.append(host_connection)

        self._connected = True

    def _discover_hosts(self):
        '''Event to discover new available hosts.'''
        self._host_list = []
        discover_event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_DISCOVER_HOST
        )

        self.event_manager.publish(
            discover_event,
            callback=self._host_discovered
        )

    def on_ready(self, callback, time_out=3):
        self.__callback = callback
        self.discover_hosts(time_out=time_out)
