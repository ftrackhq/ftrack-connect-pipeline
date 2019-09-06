# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

import threading

import logging
import ftrack_api

logger = logging.getLogger(__name__)

from qtpy import QtCore


class EventManager(object):
    '''Manages the events handling.'''
    def __init__(self, session):
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.session = session

    def publish(self, event, callback=None, remote=False):
        '''Emit *event* and provide *callback* function.'''

        if not remote:
            result = self.session.event_hub.publish(
                event,
                synchronous=True,
            )

            if result:
                result = result[0]

            # Mock async event reply.
            event_result = ftrack_api.event.base.Event(
                topic=u'ftrack.meta.reply',
                data=result,
                in_reply_to_event=event['id'],
            )

            if callback:
                callback(event_result)

        else:
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
