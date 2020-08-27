# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline import client
from ftrack_connect_pipeline.constants import asset as asset_const


class AssetManagerClient(client.Client):
    '''
    Base client class.
    '''

    @property
    def event_manager(self):
        '''Returns event_manager'''
        return self._event_manager

    @property
    def ftrack_asset_list(self):
        '''Return the current list of asset_info'''
        return self._ftrack_asset_list

    def __init__(self, event_manager):
        '''Initialise AssetManagerClient with *event_manager*

        *event_manager* should be the
        :class:`ftrack_connect_pipeline.event.EventManager`instance to
        communicate to the event server.
        '''
        super(AssetManagerClient, self).__init__(event_manager)
        self._reset_asset_list()

    def change_host(self, host_connection):
        ''' Sets the given *host_connection* as the current host connection '''
        super(AssetManagerClient, self).change_host(host_connection)

        self.schemas = [
            schema for schema in self.host_connection.definitions['schema']
            if schema.get('title').lower() == 'asset_manager'
        ]
        #Only one schema available for now, we Don't have a schema selector
        # on the AM
        schema = self.schemas[0]
        schema_title = schema.get('title').lower()
        definitions = self.host_connection.definitions.get(schema_title)
        #Only one definition for now, we don't have a definition schema on the
        # AM
        self.definition = definitions[0]
        self.engine_type = self.definition['_config']['engine_type']

        self.menu_action_plugins = self.definition.get('actions')
        self.discover_plugins = self.definition.get('discover')

    def _reset_asset_list(self):
        '''Empty the _ftrack_asset_list'''
        self._ftrack_asset_list = []

    def discover_assets(self, plugin=None):
        '''
        Discover assets on the scene
        '''
        self._reset_asset_list()
        data = {'method': 'discover_assets',
                'plugin': plugin}
        self.host_connection.run(
            data, self.engine_type, self._asset_discovered_callback
        )

    def _asset_discovered_callback(self, event):
        '''callback, Assets discovered'''
        if not event['data']:
            return
        for ftrack_asset in event['data']:
            if ftrack_asset not in self.ftrack_asset_list:
                ftrack_asset['session'] = self.session
                self._ftrack_asset_list.append(ftrack_asset)
        self._connected = True

    def change_version(self, asset_info, new_version_id):
        '''
        Change the current version of the given *asset_info* to the
        given *new_version_id*
        '''

        data = {'method': 'change_version',
                'plugin': None,
                'assets': asset_info,
                'options': {'new_version_id': new_version_id}
                }
        self.host_connection.run(
            data, self.engine_type, self._change_version_callback
        )
    def _change_version_callback(self, event):
        '''
        Change version callback, updates the current ftrack_asset_list
        '''
        if not event['data']:
            return
        data = event['data']
        for k, v in data.items():
            old_info_id = k
            index = None
            i = 0
            for asset_info in self.ftrack_asset_list:
                if asset_info[asset_const.ASSET_INFO_ID] == old_info_id:
                    index = i
                    break
                i += 1
            if index != None:
                self.ftrack_asset_list[index] = v

    def select_assets(self, asset_info_list):
        '''
        Select the assets of the given *asset_info_list*
        '''
        data = {'method': 'select_assets',
                'plugin': None,
                'assets': asset_info_list
                }
        self.host_connection.run(data, self.engine_type)

    def remove_assets(self, asset_info_list):
        '''
        Remove the assets of the given *asset_info_list*
        '''
        data = {'method': 'remove_assets',
                'plugin': None,
                'assets': asset_info_list
                }
        self.host_connection.run(
            data, self.engine_type, self._remove_assets_callback
        )

    def _remove_assets_callback(self, event):
        '''
        remove_assets callback, updates the current ftrack_asset_list
        '''
        if not event['data']:
            return
        data = event['data']
        for k, v in data.items():
            old_info_id = k
            index = None
            i = 0
            for asset_info in self.ftrack_asset_list:
                if asset_info[asset_const.ASSET_INFO_ID] == old_info_id:
                    index = i
                    break
                i += 1
            if index != None:
                self.ftrack_asset_list.pop(index)

    def update_assets(self, asset_info_list, plugin):
        '''
        Updates the assets from the given *asset_info_list* using the given
        *plugin*
        '''
        data = {'method': 'update_assets',
                'plugin': plugin,
                'assets': asset_info_list
                }
        self.host_connection.run(
            data, self.engine_type, self._update_assets_callback
        )

    def _update_assets_callback(self, event):
        '''
        update_assets callback. it updates the current ftrack_asset_list
        '''
        if not event['data']:
            return
        data = event['data']
        for k, v in data.items():
            old_info_id = k
            index = None
            i=0
            for asset_info in self.ftrack_asset_list:
                if asset_info[asset_const.ASSET_INFO_ID] == old_info_id:
                    index = i
                    break
                i+=1
            if index != None:
                self.ftrack_asset_list[index] = v.get(v.keys()[0])