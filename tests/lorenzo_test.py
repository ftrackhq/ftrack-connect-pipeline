import logging
import os
from ftrack_connect_pipeline import client, host, constants
from ftrack_connect_pipeline.session import get_shared_session


event_paths = [
    'ftrack-connect-pipeline/resource/application_hook',
    'ftrack-connect-pipeline-definition/resource/application_hook'
]

os.environ['FTRACK_EVENT_PLUGIN_PATH'] = os.pathsep.join(event_paths)

session = get_shared_session()
host_id = host.initialise(session, host=constants.HOST)
baseClient = client.BasePipelineClient(session, ui=constants.UI)


def on_connect(client):
    print 'packages:', client.packages


def on_ready(client):
    hosts = client.hosts
    host_id = hosts[0]
    print 'HOSTID:', host_id
    client.connect(host_id, on_connect)


baseClient.ready(on_ready)