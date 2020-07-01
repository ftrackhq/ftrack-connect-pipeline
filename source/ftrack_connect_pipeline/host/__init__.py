# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import uuid
import ftrack_api
import logging

from ftrack_connect_pipeline.host import engine
from ftrack_connect_pipeline.host import validation
from ftrack_connect_pipeline import constants, utils
from ftrack_connect_pipeline.constants import asset as asset_const
from ftrack_connect_pipeline.host import engine


from functools import partial


logger = logging.getLogger(__name__)


def provide_host_information(hostid, definitions, event):
    '''return the current hostid'''
    logger.debug('providing host_id: {}'.format(hostid))
    context_id = utils.get_current_context()
    host_dict = {
        'host_id': hostid,
        'context_id': context_id,
        'definition': definitions
    }
    return host_dict


class Host(object):

    host = [constants.HOST]
    asset_manager_engine = engine.AssetManagerEngine

    def __repr__(self):
        return '<Host:{0}>'.format(self.hostid)

    def __del__(self):
        self.logger.debug('Closing {}'.format(self))

    @property
    def hostid(self):
        '''Return current hostid'''
        return self._hostid

    @property
    def session(self):
        '''Return session'''
        return self._event_manager.session

    def __init__(self, event_manager):
        '''Initialise Host Class with *event_manager* and *host*(optional)

        *event_manager* should be the
        :class:`ftrack_connect_pipeline.event.EventManager`instance to
        communicate to the event server.

        *host* is a list of valid host definitions.(optional)'''
        super(Host, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._hostid = '{}-{}'.format('.'.join(self.host), uuid.uuid4().hex)

        self.logger.info(
            'initializing {}'.format(self)
        )
        self._event_manager = event_manager
        self.register()
        self.listen_asset_manager()

    def get_engine_runner(self, schema_engine, asset_type=None):
        MyEngine = engine.getEngine(engine.BaseEngine, schema_engine)
        engine_runner = MyEngine(self._event_manager, self.host, self.hostid,
                                 asset_type)
        return engine_runner

    def run(self, event):
        #TODO: to know that comes from the asset manager, we can filter by
        # data[topic] so we will know if it comes from the topic
        # client.am.discover_assets for example, and that means that we already
        # have the action to run, so we can do something like
        # eval("{}.{}".format(engine_runner, event_topic_splited).

        data = event['data']['pipeline']['data']

        try:
            validation.validate_schema(self.__registry['schema'], data)
        except Exception as error:
            self.logger.error("Can't validate the data {} "
                              "error: {}".format(data, error))
            return False

        asset_type = self.get_asset_type_from_packages(
            self.__registry['package'], data['package'])
        schema_engine = data['_config']['engine']

        engine_runner = self.get_engine_runner(schema_engine, asset_type)
        runnerResult = engine_runner.run(data)

        if runnerResult == False:
            self.logger.error("Couldn't publish the data {}".format(data))

        return runnerResult

    # def run_asset_action(self, event):
    #     data = event['data']['pipeline']
    #     schema_engine = 'AssetManagerEngine'
    #     #TODO: the get engine seems to not be working for the loader and publisher
    #     MyEngine = engine.getEngine(engine.BaseEngine, schema_engine)
    #     print "MMyEngine --> {}".format(MyEngine)
    #     engine_runner = MyEngine(
    #         self._event_manager, self.host, self.hostid
    #     )
    #     runnerResult = engine_runner.run(data)
    #
    #     if runnerResult == False:
    #         self.logger.error(
    #             "Couldn't run the action for the data {}".format(data)
    #         )
    #
    #     return runnerResult

    def _run_discover_assets(self, event):
        data = event['data']['pipeline']
        # TODO: the get engine seems to not be working for the loader and publisher

        engine_runner = self.get_engine_runner(
            self.asset_manager_engine.__name__
        )

        runnerResult = engine_runner.discover_assets(data)

        if runnerResult == False:
            self.logger.error(
                "Couldn't run the action for the data {}".format(data)
            )

        return runnerResult

    def _run_change_asset_version(self, event):
        data = event['data']['pipeline']
        # TODO: the get engine seems to not be working for the loader and publisher

        engine_runner = self.get_engine_runner(
            self.asset_manager_engine.__name__
        )

        runnerResult = engine_runner.change_asset_version(data)

        if runnerResult == False:
            self.logger.error(
                "Couldn't run the action for the data {}".format(data)
            )

        return runnerResult

    def _run_clear_selection(self, event):
        data = event['data']['pipeline']

        engine_runner = self.get_engine_runner(
            self.asset_manager_engine.__name__
        )

        runnerResult = engine_runner.clear_selection(data)

        if runnerResult == False:
            self.logger.error(
                "Couldn't run the action for the data {}".format(data)
            )

        return runnerResult

    def _run_select_asset(self, event):
        data = event['data']['pipeline']

        engine_runner = self.get_engine_runner(
            self.asset_manager_engine.__name__
        )

        runnerResult = engine_runner.select_asset(data)

        if runnerResult == False:
            self.logger.error(
                "Couldn't run the action for the data {}".format(data)
            )

        return runnerResult

    def _run_remove_asset(self, event):
        print "event ---> {}".format(event)
        data = event['data']['pipeline']

        engine_runner = self.get_engine_runner(
            self.asset_manager_engine.__name__
        )

        runnerResult = engine_runner.remove_asset(data)

        if runnerResult == False:
            self.logger.error(
                "Couldn't run the action for the data {}".format(data)
            )

        return runnerResult

    def get_asset_type_from_packages(self, packages, data_package):
        for package in packages:
            if package['name'] == data_package:
                return package['asset_type']

    def on_register_definition(self, event):
        '''Register definition coming from *event* and store them.'''
        raw_result = event['data']

        if not raw_result:
            return

        validated_result = self.validate(raw_result)

        for key, value in validated_result.items():
            logger.info('Valid packages : {} : {}'.format(key, len(value)))

        self.__registry = validated_result

        handle_event = partial(
            provide_host_information,
            self.hostid,
            validated_result
        )

        self._event_manager.subscribe(
            constants.PIPELINE_DISCOVER_HOST,
            handle_event
        )

        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_HOST_RUN, self.hostid
            ),
            self.run
        )
        self.logger.info('host {} ready.'.format(self.hostid))

    def validate(self, data):

        plugin_validator = validation.PluginDiscoverValidation(
            self.session, self.host
        )

        invalid_publishers_idxs = plugin_validator.validate_publishers_plugins(
            data['publisher'])
        if invalid_publishers_idxs:
            for idx in sorted(invalid_publishers_idxs, reverse=True):
                data['publisher'].pop(idx)

        invalid_loaders_idxs = plugin_validator.validate_loaders_plugins(
            data['loader'])
        if invalid_loaders_idxs:
            for idx in sorted(invalid_loaders_idxs, reverse=True):
                    data['loader'].pop(idx)

        return data

    def register(self):
        '''register package'''

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_REGISTER_TOPIC,
            data={
                'pipeline': {
                    'type': 'definition',
                    'host': self.host[-1],
                }
            }
        )

        self._event_manager.publish(
            event,
            self.on_register_definition
        )

    def listen_asset_manager(self):

        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_DISCOVER_ASSETS, self.hostid
            ),
            self._run_discover_assets
        )
        self.logger.info(
            'subscribe to asset manager version changed  {} ready.'.format(
                self.hostid
            )
        )


        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_ASSET_VERSION_CHANGED, self.hostid
            ),
            self._run_change_asset_version
        )
        self.logger.info(
            'subscribe to asset manager version changed  {} ready.'.format(
                self.hostid
            )
        )

        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_ON_SELECT_ASSET, self.hostid
            ),
            self._run_select_asset
        )
        self.logger.info(
            'subscribe to asset manager version changed  {} ready.'.format(
                self.hostid
            )
        )

        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_ON_REMOVE_ASSET, self.hostid
            ),
            self._run_remove_asset
        )
        self.logger.info(
            'subscribe to asset manager version changed  {} ready.'.format(
                self.hostid
            )
        )

        self._event_manager.subscribe(
            '{} and data.pipeline.host_id={}'.format(
                constants.PIPELINE_ON_CLEAR_SELECTION, self.hostid
            ),
            self._run_clear_selection
        )
        self.logger.info(
            'subscribe to asset manager version changed  {} ready.'.format(
                self.hostid
            )
        )

    def reset(self):
        self._host = []
        self._hostid = None
        self.__registry = {}






