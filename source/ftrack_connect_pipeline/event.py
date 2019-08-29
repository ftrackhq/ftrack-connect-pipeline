# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import threading
import uuid
import logging
import ftrack_api

logger = logging.getLogger(__name__)

from qtpy import QtCore


class _EventThread(threading.Thread):
    '''Wrapper object to simulate asyncronus events.'''
    def __init__(self, session, event, callback=None):
        super(_EventThread, self).__init__(target=self.run)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._callback = callback
        self._event = event
        self._session = session
        self._result = {}

    def run(self):
        '''Target thread method.'''
        result = self._session.event_hub.publish(
            self._event,
            synchronous=True,
        )

        if result:
            result = result[0]

        # Mock async event reply.
        event = ftrack_api.event.base.Event(
            topic=u'ftrack.meta.reply',
            data=result,
            in_reply_to_event=self._event['id'],
        )

        if self._callback:
            self._callback(event)


class EventManager(object):
    '''Manages the events handling.'''

    @property
    def session(self):
        return self._session

    @property
    def ui(self):
        return self._ui

    @property
    def host(self):
        return self._host

    @property
    def hostid(self):
        return self._hostid

    @property
    def remote(self):
        return self._remote

    def __init__(self, session, remote, ui=None, host=None):
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self._session = session
        self._ui = ui
        self._host = host
        self._hostid = '{}-{}-{}'.format(host, ui, uuid.uuid4().hex)

        self._remote = remote

    def publish(self, event, callback=None, remote=None):
        '''Emit *event* and provide *callback* function.'''

        is_remote = remote if remote is not None else self.remote

        if not is_remote:
            self.logger.debug('running event {} local'.format(event))
            event_thread = _EventThread(self.session, event, callback)
            event_thread.start()

        else:
            self.logger.debug('running event {} remote'.format(event))
            self.session.event_hub.publish(
                event,
                on_reply=callback
            )


class NewApiEventHubThread(QtCore.QThread):
    '''Listen for events from ftrack's event hub.'''

    def __init__(self, parent=None):
        super(NewApiEventHubThread, self).__init__(parent=parent)
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def start(self, session):
        '''Start thread for *_session*.'''
        self._session = session
        self.logger.debug('Starting event hub thread.')
        super(NewApiEventHubThread, self).start()

    def run(self):
        '''Listen for events.'''
        self.logger.debug('Event hub thread started.')
        self._session.event_hub.wait()
