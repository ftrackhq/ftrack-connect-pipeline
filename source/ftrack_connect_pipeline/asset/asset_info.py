# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

import logging
import json
from ftrack_connect_pipeline.constants import asset as constants


def generate_asset_info_dict_from_args(context, data, options, session):
    '''
    Returns a diccionary constructed from the needed values of the given
    *context*, *data* and *options*

    *context* Context dictionary of the current asset. Should contain the keys
    asset_type, asset_name, asset_id, version_number, version_id, context_id.
    *data* Data of the current operation or plugin. Should contain the
    component_path from the asset that we are working on.
    *options* Options of the current widget or operation, should contain the
    load_mode that we want to/or had apply to the current asset.
    *session* should be the :class:`ftrack_api.session.Session` instance
    to use for communication with the server.
    '''
    arguments_dict = {}

    arguments_dict[constants.ASSET_NAME] = context.get(
        'asset_name', 'No name found'
    )
    arguments_dict[constants.ASSET_TYPE] = context.get('asset_type', '')
    arguments_dict[constants.ASSET_ID] = context.get('asset_id', '')
    arguments_dict[constants.VERSION_NUMBER] = int(
        context.get('version_number', 0)
    )
    arguments_dict[constants.VERSION_ID] = context.get('version_id', '')

    arguments_dict[constants.LOAD_MODE] = options.get('load_mode', '')

    arguments_dict[constants.ASSET_INFO_OPTIONS] = options.get(
        constants.ASSET_INFO_OPTIONS, ''
    )

    asset_version = session.get(
        'AssetVersion', arguments_dict[constants.VERSION_ID]
    )

    location = session.pick_location()

    for component in asset_version['components']:
        if location.get_component_availability(component) < 100.0:
            continue
        component_path = location.get_filesystem_path(component)
        if component_path in data:
            arguments_dict[constants.COMPONENT_NAME] = component['name']
            arguments_dict[constants.COMPONENT_ID] = component['id']
            arguments_dict[constants.COMPONENT_PATH] = component_path

    return arguments_dict


class FtrackAssetInfo(dict):
    '''
    Base FtrackAssetInfo class.
    '''

    @property
    def is_deprecated(self):
        '''
        Returns whether the current class is maded up from a legacy mapping type
        of the asset_information.
        '''
        return self._is_deprecated_version

    def _conform_data(self, mapping):
        new_mapping = {}
        for k in constants.KEYS:
            v = mapping.get(k)
            new_mapping.setdefault(k, v)
        return new_mapping

    def __init__(self, mapping=None, **kwargs):
        '''
        Initialize the FtrackAssetInfo with the given *mapping*.

        *mapping* Dictionary with the current asset information.
        '''
        self.logger = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )

        self._is_deprecated_version = False
        mapping = mapping or {}
        mapping = self._conform_data(mapping)
        super(FtrackAssetInfo, self).__init__(mapping, **kwargs)

    def encode_options(self, asset_info_options):
        '''Encodes the json value from the given *asset_info_opitons
        to base64'''
        return json.dumps(asset_info_options).encode('base64')

    def decode_options(self, asset_info_options):
        '''Decodes the json value from the given *asset_info_opitons
        from base64'''
        return json.loads(asset_info_options.decode('base64'))

    def __getitem__(self, k):
        '''In case of the given *k* is the asset_info_options it will
        automatically return the decoded json'''
        value = super(FtrackAssetInfo, self).__getitem__(k)
        if k == constants.ASSET_INFO_OPTIONS:
            value = self.decode_options(value)
        return value

    def __setitem__(self, k, v):
        '''In case of the given *k* is the asset_info_options it will
        automatically encode the given json value to base64'''
        if k == constants.ASSET_INFO_OPTIONS:
            v = self.encode_options(v)
        super(FtrackAssetInfo, self).__setitem__(k, v)

    @classmethod
    def from_ftrack_version(cls, ftrack_version, component_name):
        '''
        Return an FtrackAssetInfo object generated from the given *ftrack_version*
        and the given *component_name*
        '''
        asset_info_data = {}
        asset = ftrack_version['asset']
        asset_info_data[constants.ASSET_NAME] = asset['name']
        asset_info_data[constants.ASSET_TYPE] = asset['type']['name']
        asset_info_data[constants.ASSET_ID] = asset['id']
        asset_info_data[constants.VERSION_NUMBER] = int(
            ftrack_version['version'])
        asset_info_data[constants.VERSION_ID] = ftrack_version['id']

        location = ftrack_version.session.pick_location()

        for component in ftrack_version['components']:
            if component['name'] == component_name:
                if location.get_component_availability(component) == 100.0:
                    component_path = location.get_filesystem_path(component)
                    if component_path:
                        asset_info_data[constants.COMPONENT_NAME] = component[
                            'name']
                        asset_info_data[constants.COMPONENT_ID] = component[
                            'id']
                        asset_info_data[
                            constants.COMPONENT_PATH] = component_path

        return cls(asset_info_data)