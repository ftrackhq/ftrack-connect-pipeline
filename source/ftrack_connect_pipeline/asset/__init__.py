# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import logging
import ftrack_api
from ftrack_connect_pipeline.asset.asset_info import FtrackAssetInfo, asset_info_from_ftrack_version
from ftrack_connect_pipeline.constants import asset as asset_const
from ftrack_connect_pipeline import constants


class FtrackAssetBase(object):
    '''
        Base FtrackAssetBase class.
    '''

    identity = None
    default_component_name = 'main'

    def is_ftrack_node(self, other):
        raise NotImplementedError()

    @property
    def component_name(self):
        return self.asset_info.get(asset_const.COMPONENT_NAME, self.default_component_name)

    @property
    def asset_versions(self):
        query = (
            'select is_latest_version, id, asset, components, components.name, components.id, version, asset , asset.name, asset.type.name from '
            'AssetVersion where asset.id is "{}" and components.name is "{}"'
            'order by version ascending'
        ).format(
            self.asset_info[asset_const.ASSET_ID], self.component_name
        )
        versions = self.session.query(query).all()
        return versions

    @property
    def ftrack_version(self):
        asset_version = self.session.get(
            'AssetVersion', self.asset_info[asset_const.VERSION_ID]
        )
        return asset_version

    @property
    def is_latest(self):
        return self.ftrack_version['is_latest_version']

    @property
    def asset_info(self):
        return self._asset_info

    @property
    def session(self):
        return self.event_manager.session

    @property
    def event_manager(self):
        return self._event_manager

    @property
    def nodes(self):
        return self._nodes[:]

    @property
    def node(self):
        return self._node

    def __init__(self, event_manager):
        '''
        Initialize FtrackAssetBase with *ftrack_asset_info*, and *session*.

        *ftrack_asset_info* should be the
        :class:`ftrack_connect_pipeline.asset.asset_info.FtrackAssetInfo`
        instance.
        *session* should be the :class:`ftrack_api.session.Session` instance
        to use for communication with the server.
        '''
        super(FtrackAssetBase, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._asset_info = None#ftrack_asset_info
        self._event_manager = event_manager

        self._nodes = []
        self._node = None

    def init_node(self):
        '''
        Return the ftrack node for this class. It checks if there is already a
        matching ftrack node in the scene, in this case it updates the node if
        it's not. In case there is no node in the scene this function creates a
        new one.
        '''
        self._set_node(None)
        return self.node

    def set_asset_info(self, ftrack_asset_info):
        ''' Sets the self._asset_info from the given *ftrack_asset_info*'''
        if not isinstance(ftrack_asset_info, FtrackAssetInfo):
            raise TypeError(
                "ftrack_asset_info argument has to be type of FtrackAssetInfo"
            )
        self._asset_info = ftrack_asset_info

    def _set_node(self, ftrack_node):
        '''
        Sets the given *ftrack_node* as the current self.node of the class
        '''
        self._node = ftrack_node

    def change_version(self, asset_version_id, host_id):
        '''
        Publish the PIPELINE_ASSET_VERSION_CHANGED event for the given *host_id*
        with the asset info of the given *asset_version_id*.

        note:: Public function to change the asset version, it's been called from
        the api or from the asset manager UI '''
        #TODO: Is better to get the asset_info here so we don't have to pass
        # the component name around
        asset_version = self.session.get('AssetVersion', asset_version_id)
        asset_info = asset_info_from_ftrack_version(
            asset_version, self.component_name
        )

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_ASSET_VERSION_CHANGED,
            data={
                'pipeline': {
                    'host_id': host_id,
                    'data': asset_info
                }
            }
        )
        self._event_manager.publish(event, self._change_version)

    def _change_version(self, event):
        '''
        Callback function to change the asset version from the given *event*
        '''
        asset_info = event['data']

        if not asset_info:
            self.logger.warning("Asset version couldn't change")
            return
        if not isinstance(asset_info, FtrackAssetInfo):
            raise TypeError(
                "return type of change version has to be type of FtrackAssetInfo"
            )

        self.asset_info.update(asset_info)

        return asset_info

    def discover_assets(self):
        '''
        Base discover assets function.
        '''
        #TODO: THIS is just for testing remove this later, we could add some
        # arguments to pass to the function and customize the discover in case
        # we do it from the API. Or maybe it's simply unuseful
        from ftrack_connect_pipeline.asset.asset_info import asset_info_from_ftrack_version

        component_name = 'main'
        versions = self.session.query(
            'select id, components, components.name, components.id, version, '
            'asset , asset.name, asset.type.name from AssetVersion where '
            'asset_id != None and components.name is "{0}" limit 10'.format(
                component_name
            )
        ).all()

        component_name = 'main'

        ftrack_asset_info_list = []

        for version in versions:
            asset_info = asset_info_from_ftrack_version(version, component_name)
            ftrack_asset_info_list.append(asset_info)

        return ftrack_asset_info_list

    def clear_selection(self, host_id):
        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_ON_SELECT_ASSET,
            data={
                'pipeline': {
                    'host_id': host_id,
                    'data': self
                }
            }
        )
        self._event_manager.publish(event, self._clear_selection)

    def _clear_selection(self, event):
        # self.logger.error("Not implemented on API")
        asset_item = event['data']
        return asset_item

    def select_asset(self, host_id):
        '''
        Publish the PIPELINE_ASSET_VERSION_CHANGED event for the given *host_id*
        with the asset info of the given *asset_version_id*.

        note:: Public function to change the asset version, it's been called from
        the api or from the asset manager UI '''

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_ON_SELECT_ASSET,
            data={
                'pipeline': {
                    'host_id': host_id,
                    'data': self
                }
            }
        )
        self._event_manager.publish(event, self._select_asset)

    def _select_asset(self, event):
        #self.logger.error("Not implemented on API")
        asset_item = event['data']
        return asset_item

    def remove_asset(self, host_id):
        '''
        Publish the PIPELINE_ASSET_VERSION_CHANGED event for the given *host_id*
        with the asset info of the given *asset_version_id*.

        note:: Public function to change the asset version, it's been called from
        the api or from the asset manager UI '''

        event = ftrack_api.event.base.Event(
            topic=constants.PIPELINE_ON_REMOVE_ASSET,
            data={
                'pipeline': {
                    'host_id': host_id,
                    'data': self
                }
            }
        )
        self._event_manager.publish(event, self._remove_asset)

    def _remove_asset(self, event):
        '''
        Callback function to change the asset version from the given *event*
        '''
        asset_item = event['data']

        if not asset_item == self:
            self.logger.error("asset_item is not equal to self")

        return asset_item

