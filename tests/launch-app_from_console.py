import os
from ftrack_connect_pipeline import host, constants, event
import ftrack_api

# Create a session and Event Manager
session = ftrack_api.Session(auto_connect_event_hub=False)
event_manager = event.EventManager(
    session=session, mode=constants.LOCAL_EVENT_MODE
)
import os
import sys
import logging
cwd = os.path.dirname(__file__)
sources = "/Users/ftrack/work/ftrack/repos/ftrack-application-launcher/build/ftrack-application-launcher-1.0.0-b5/dependencies"
sys.path.append(sources)
import ftrack_api
from ftrack_application_launcher.discover_applications import DiscoverApplications

default_config_path = "/Users/ftrack/work/ftrack/repos/ftrack-application-launcher/resource/config"
# Ensure the config path is in form of a list
config_paths = os.environ.setdefault(
    'FTRACK_APPLICATION_LAUNCHER_CONFIG_PATHS',
    default_config_path
).split(os.path.pathsep)

applications = DiscoverApplications(session, config_paths)
applications.register()

maya_action = applications._actions[5]

maya_idetifier = maya_action.launcher.applicationStore.applications[0]['identifier']

#TODO: were this context come from?????
context = {'actionIdentifier': 'ftrack-connect-launch-maya', 'label': 'Maya', 'icon': 'https://ftrack-integrations.ftrackapp.com/application_icons/maya.png', 'variant': '2022 [pipeline]', 'applicationIdentifier': 'maya_2022 [pipeline]', 'integrations': {'pipeline': ['ftrack-connect-pipeline-definition', 'ftrack-connect-pipeline', 'ftrack-connect-pipeline-qt', 'ftrack-connect-pipeline-maya']}, 'host': 'LLUISs-MacBook-Pro-14.local', 'selection': [{'entityId': '432343de-a6a6-11ec-935c-be6e0a48ed73', 'entityType': 'task'}], 'source': {'id': 'cd6904b699dc4042a39709268e5e6126', 'user': {'username': 'lluis.casals@ftrack.com'}}}

maya_action.launcher.launch(maya_idetifier, context)
# Succesfully launch maya but not with the framework pre-loaded