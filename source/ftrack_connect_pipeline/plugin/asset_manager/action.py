# :coding: utf-8
# :copyright: Copyright (c) 2014-2020 ftrack

from ftrack_connect_pipeline.asset import FtrackAssetBase
from ftrack_connect_pipeline import constants
from ftrack_connect_pipeline.plugin import base

class AssetManagerActionPlugin(base.BaseActionPlugin):
    ''' Class representing a Collector Plugin

    .. note::

        _required_output a List
    '''
    return_type = list
    plugin_type = constants.PLUGIN_AM_ACTION_TYPE
    _required_output = []
    ftrack_asset_class = FtrackAssetBase

    def __init__(self, session):
        '''Initialise CollectorPlugin with *session*

        *session* should be the :class:`ftrack_api.session.Session` instance
        to use for communication with the server.
        '''
        super(AssetManagerActionPlugin, self).__init__(session)