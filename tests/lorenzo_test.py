import logging
import os
from ftrack_connect_pipeline import client, host, constants
from ftrack_connect_pipeline.session import get_shared_session

logging.basicConfig(level=logging.DEBUG)

event_paths = [
    '/home/ftrackwork/devel/components/PLUGINS/PIPELINE/ftrack-connect-pipeline/resource/application_hook',
    '/home/ftrackwork/devel/components/PLUGINS/PIPELINE/ftrack-connect-pipeline-definition/resource/application_hook'
]

os.environ['FTRACK_EVENT_PLUGIN_PATH'] = os.pathsep.join(event_paths)

session = get_shared_session()
host_id = host.initialise(session, host=constants.HOST, ui=constants.UI)
baseClient = client.BasePipelineClient(session, host=constants.HOST, ui=constants.UI)


def my_callback(client):
    print client.initalised
    print client.packages


baseClient.connect(host_id, my_callback)