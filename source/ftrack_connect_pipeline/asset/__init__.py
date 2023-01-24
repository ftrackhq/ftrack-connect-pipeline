# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack
import copy
import logging
import unicodedata
import re
import os

from ftrack_connect_pipeline.asset.asset_info import (
    FtrackAssetInfo,
    generate_asset_info_dict_from_args,
)
from ftrack_connect_pipeline.asset.dcc_object import DccObject
from ftrack_connect_pipeline.constants import asset as asset_const


class FtrackObjectManager(object):
    '''
    FtrackObjectManager class.
    Mantain the syncronization between asset_info and the ftrack information of
    the objects in the scene.
    '''

    DccObject = DccObject

    @property
    def asset_info(self):
        '''
        Returns instance of
        :class:`~ftrack_connect_pipeline.asset.FtrackAssetInfo`
        '''
        return self._asset_info

    @asset_info.setter
    def asset_info(self, value):
        '''
        Sets the self :obj:`asset_info`,
        *value* :class:`~ftrack_connect_pipeline.asset.FtrackAssetInfo`
        '''
        if not isinstance(value, FtrackAssetInfo):
            try:
                value = FtrackAssetInfo(value)
            except Exception:
                raise ValueError(
                    'Could not initialise asset info from {}!'.format(value)
                )

        self._asset_info = value

    @property
    def dcc_object(self):
        '''
        Returns instance of
        :class:`~ftrack_connect_pipeline.asset.DccObject`
        '''
        return self._dcc_object

    @dcc_object.setter
    def dcc_object(self, value):
        '''
        Sets the self :obj:`dcc_object`,
        *value* :class:`~ftrack_connect_pipeline.asset.DccObject`
        '''
        if not isinstance(value, self.DccObject):
            raise ValueError(
                'DccObject {} should be instance of '
                ':class:`~ftrack_connect_pipeline.asset.DccObject`'
            )
        if not self._check_sync(value):
            self._sync(value)
        self._dcc_object = value

    @property
    def session(self):
        '''
        Returns instance of :class:`ftrack_api.session.Session`
        '''
        return self.event_manager.session

    @property
    def event_manager(self):
        '''Returns instance of
        :class:`~ftrack_connect_pipeline.event.EventManager`'''
        return self._event_manager

    @property
    def is_sync(self):
        '''Returns if the self :obj:`dcc_object` is sync with the
        self :obj:`asset_info`'''
        return self._check_sync(self.dcc_object)

    @property
    def objects_loaded(self):
        '''
        Returns whether the objects are loaded in the scene or not.
        '''
        return self.asset_info[asset_const.OBJECTS_LOADED]

    @objects_loaded.setter
    def objects_loaded(self, value):
        '''
        Set the self :obj:`asset_info` as objects_loaded.
        '''
        self.asset_info[asset_const.OBJECTS_LOADED] = value
        if self.dcc_object:
            self.dcc_object.objects_loaded = value

    @property
    def is_snapshot(self):
        '''
        Returns whether the objects are loaded in the scene or not.
        '''
        return self.asset_info[asset_const.IS_SNAPSHOT]

    @is_snapshot.setter
    def is_snapshot(self, value):
        '''
        Set the self :obj:`asset_info` as is_snapshot.
        '''
        self.asset_info[asset_const.IS_SNAPSHOT] = value
        if self.dcc_object:
            self.dcc_object.is_snapshot = value

    def __init__(self, event_manager):
        '''
        Initialize FtrackObjectManager with instance of
        :class:`~ftrack_connect_pipeline.event.EventManager`
        '''
        super(FtrackObjectManager, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._asset_info = None
        self._dcc_object = None
        self._event_manager = event_manager

    def _generate_dcc_object_name(self):
        '''
        Returns a name for the current self :obj:`dcc_object` based on
        the first 2 and last 2 characters of the
        :constant:`asset_const.ASSET_INFO_ID`
        '''
        short_id = "{}{}".format(
            self.asset_info[asset_const.ASSET_INFO_ID][:2],
            self.asset_info[asset_const.ASSET_INFO_ID][-2:],
        )
        # Make sure the name contains valid characters
        name_value = self.asset_info[asset_const.CONTEXT_PATH]
        name_value = unicodedata.normalize('NFKD', str(name_value)).encode(
            'ascii', 'ignore'
        )
        name_value = re.sub('[^\w\.-]', "_", name_value.decode('utf-8'))

        dcc_object_name = asset_const.DCC_OBJECT_NAME.format(
            name_value,
            short_id,
        )

        return str(dcc_object_name.strip().lower())

    def _check_sync(self, dcc_object):
        '''
        Check if the parameters of the given *dcc_object* match the
        values of the current self :obj:`asset_info`.
        '''
        if not isinstance(dcc_object, self.DccObject):
            raise ValueError(
                'DccObject {} should be instance of '
                ':class:`~ftrack_connect_pipeline.asset.DccObject`'
            )

        synced = False

        node_asset_info = FtrackAssetInfo(dcc_object)

        if node_asset_info == self.asset_info:
            self.logger.debug("{} is synced".format(dcc_object.name))
            synced = True

        return synced

    def _sync(self, dcc_object):
        '''
        Updates the parameters of the given *dcc_object* based on the
        self :obj:`asset_info`.
        '''
        dcc_object.update(self.asset_info)

    def connect_objects(self, objects):
        '''
        Link the given *objects* ftrack attribute to the self
        :obj:`dcc_object`.

        *objects* List of objects
        '''
        self.dcc_object.connect_objects(objects)

    def create_new_dcc_object(self):
        '''
        Creates a new dcc_object with a unique name.
        '''
        name = self._generate_dcc_object_name()
        dcc_object = self.DccObject(name)

        self.dcc_object = dcc_object

        return self.dcc_object

    def generate_snapshot_asset_info_options(
        self, context_data, data, loader_options
    ):
        '''
        Returns a dictionary of options for creating a snapshot asset_info.
        '''
        return {
            "pipeline": {
                "plugin_name": loader_options['plugin_name'],
                "plugin_type": loader_options['plugin_type'],
                "method": loader_options['method'],
                "category": "plugin",
                "host_type": "unreal",
                "definition": loader_options['definition'],
            },
            "settings": {
                "context_data": context_data,
                "data": data,
                "options": {"file_formats": loader_options['file_formats']},
            },
        }

    def generate_snapshot_asset_info(
        self,
        context_data,
        asset_version_id,
        component_id,
        component_name,
        component_path,
        local_component_path,
        loader_options,
    ):
        '''
        Returns a new :class:`~ftrack_connect_pipeline.asset.FtrackAssetInfo`
        '''
        # TODO: strip down to what is absolutely needed for data and asset info options
        data = [
            {
                "name": "common_context_loader_collector",
                "options": {"file_formats": loader_options['file_formats']},
                "result": [component_path],
                "status": True,
                "category": "plugin",
                "type": "collector",
                "plugin_type": "loader.collector",
                "method": "run",
                "user_data": {},
                "widget_ref": None,
                "host_id": None,
                "plugin_id": None,
            }
        ]
        # Append version ID to context data
        context_data_merged = copy.deepcopy(context_data)
        context_data_merged[asset_const.VERSION_ID] = asset_version_id
        context_data_merged[asset_const.COMPONENT_ID] = component_id
        result = FtrackAssetInfo(
            generate_asset_info_dict_from_args(
                context_data_merged,
                data,
                {asset_const.LOAD_MODE: 'import'},
                self.session,
            )
        )
        result[
            asset_const.ASSET_INFO_OPTIONS
        ] = self.generate_snapshot_asset_info_options(
            context_data_merged, data, loader_options
        )
        result[asset_const.IS_SNAPSHOT] = True
        result[asset_const.COMPONENT_ID] = component_id
        result[asset_const.COMPONENT_NAME] = component_name
        mod_date = None
        file_size = None
        if os.path.exists(local_component_path):
            mod_date = os.path.getmtime(local_component_path)
            file_size = os.path.getsize(local_component_path)
        result[asset_const.MOD_DATE] = mod_date
        result[asset_const.FILE_SIZE] = file_size
        return result
