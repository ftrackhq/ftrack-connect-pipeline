import os
from ftrack_connect_pipeline import constants, event
from ftrack_connect_pipeline_maya import host
import ftrack_api

# Create a session and Event Manager
session = ftrack_api.Session(auto_connect_event_hub=False)
event_manager = event.EventManager(
    session=session, mode=constants.LOCAL_EVENT_MODE
)

# Init host

host_class = host.MayaHost(event_manager)

# Init Client
from ftrack_connect_pipeline import client

client_connection = client.Client(event_manager)

client_connection.discover_hosts()

client_connection.change_host(client_connection.host_connections[0])

#Now we can set the context id in the host and will update in the client as well
host_class.context_id = '4f195c00-a6a6-11ec-935c-be6e0a48ed73'
#Todo: fix this, host should be able to set up the host id and update the event
# even if we are not using the host connection


# Set the context
#Todo: if client sets the context should only call the host connection and then is the host that rises the event again
#client_connection.context_id = '15b346c0-022e-11ea-bc02-ae185fc6f561'

#TODO: until here is all working on the experimental code

title = 'Publisher'
name = 'Geometry Publisher'

#TODO: Should be a method that says get definition or get schema and returns whatever you pass.
# Find publisher schema
schema = None
for schema_candidate in client_connection.host_connection.definitions['schema']:
    if schema_candidate['title'] == title:
        schema = schema_candidate
        break
if not schema:
    raise ValueError('Could not find any schema that matches the statement')

# Find File Publisher definition.
definition = None
for publisher_candidate in client_connection.host_connection.definitions['publisher']:
    if (
        publisher_candidate['name'] == name
        and publisher_candidate['host_type'] == 'maya'
    ):
        definition = publisher_candidate
        break
if not definition:
    raise ValueError(
        'Could not find any definition that matches the statement'
    )

# Assign the definition to the client
client_connection.change_definition(schema, definition)

# Execute the definition with the required engine_type.
client_connection.run_definition(
    definition, definition['_config']['engine_type']
)

