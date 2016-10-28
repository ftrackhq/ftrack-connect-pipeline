import functools

import ftrack_api

import ftrack_connect_pipeline.util
import ftrack_connect_pipeline.ui.publish_dialog


def wrap_with_events(original_function, event_fragment, session):
    '''Return wrapped *original_function* and fire before and after events.

    Events will be emmitted on *session* before and after *original_function*
    is called. The event topic will be generated based on *event_fragment* as::

        ftrack.pipeline.{event_fragment}-before
        ftrack.pipeline.{event_fragment}-after

    '''

    event_template = 'ftrack.pipeline.{0}-{1}'

    def wrapper(*args, **kwargs):
        results = session.event_hub.publish(
            ftrack_api.event.base.Event(
                topic=event_template.format(event_fragment, 'before'),
                data=dict(
                    arguments=args,
                    keyword_arguments=kwargs
                )
            ),
            synchronous=True
        )
        for result in results:
            if result:
                return result

        returned_value = original_function(*args, **kwargs)

        session.event_hub.publish(
            ftrack_api.event.base.Event(
                topic=event_template.format(event_fragment, 'after'),
                data=dict(
                    result=returned_value
                )
            ),
            synchronous=True
        )

        return returned_value

    return wrapper


def open_publish_dialog(publish_asset):
    '''Open publish dialog for *publish_asset*.'''
    dialog = ftrack_connect_pipeline.ui.publish_dialog.PublishDialog(
        label=publish_asset.label,
        description=publish_asset.description,
        publish_asset=publish_asset
    )
    dialog.exec_()


class Asset(object):
    '''Manage assets.'''

    def __init__(self, identifier, publish_asset=None, import_asset=None):
        '''Instantiate with manager for publish and import.'''
        self.publish_asset = publish_asset
        self.import_asset = import_asset
        self.identifier = identifier

    def discover_publish(self, event):
        '''Discover publish camera.'''
        item = {
            'items': [{
                'label': self.publish_asset.label,
                'icon': self.publish_asset.icon,
                'actionIdentifier': self.identifier
            }]
        }

        return item

    def launch_publish(self, event):
        '''Callback method for publish action.'''
        ftrack_connect_pipeline.util.invoke_in_main_thread(
            functools.partial(open_publish_dialog, self.publish_asset)
        )

        return {
            'success': True,
            'message': 'Custom publish action started successfully!'
        }

    def register(self, session):
        '''Register listeners on *session*.'''
        self._session = session

        self._session.event_hub.subscribe(
            'topic=ftrack.action.discover',
            self.discover_publish
        )

        self._session.event_hub.subscribe(
            'topic=ftrack.action.launch and data.actionIdentifier={0}'.format(
                self.identifier
            ),
            self.launch_publish
        )

        self.publish_asset.prepare_publish = wrap_with_events(
            self.publish_asset.prepare_publish,
            'prepare-publish',
            session
        )
        self.publish_asset.get_options = wrap_with_events(
            self.publish_asset.get_options,
            'get-options',
            session
        )
        self.publish_asset.get_item_options = wrap_with_events(
            self.publish_asset.get_item_options,
            'get-item-options',
            session
        )
        self.publish_asset.get_publish_items = wrap_with_events(
            self.publish_asset.get_publish_items,
            'get-publish-items',
            session
        )
        self.publish_asset.publish = wrap_with_events(
            self.publish_asset.publish,
            'publish',
            session
        )


class ImportAsset(object):
    '''Manage import of an asset.'''

    def discover(self, event):
        '''Discover import camera.'''
        raise NotImplementedError()

    def get_options(self, component):
        '''Return import options from *component*.'''
        return []

    def import_asset(self, component, options):
        '''Import *component* based on *options*.'''
        raise NotImplementedError()


class PublishAsset(object):
    '''Manage publish of an asset.'''

    def __init__(self, label, description, icon=None):
        '''Instantiate publish asset with *label* and *description*.'''
        self.label = label
        self.description = description
        self.icon = icon

    def discover(self, event):
        '''Discover import camera.'''
        raise NotImplementedError()

    def prepare_publish(self):
        '''Return context for publishing.'''
        return dict()

    def get_publish_items(self, publish_data):
        '''Return list of items that can be published.'''
        return []

    def get_item_options(self, publish_data, key):
        '''Return options for publishable item with *key*.'''
        return []

    def get_options(self, publish_data):
        '''Return general options for.'''
        from ftrack_connect_pipeline.ui.widget.field import asset_selector
        asset_selector = asset_selector.AssetSelector(
            ftrack_connect_pipeline.util.get_ftrack_entity()
        )

        return [{
            'widget': asset_selector,
            'type': 'qt_widget',
            'name': 'asset'
        }]

    def update_with_options(
        self, publish_data, item_options, general_options, selected_items
    ):
        '''Update *publish_data* with *item_options* and *general_options*.'''
        publish_data['options'] = general_options
        publish_data['item_options'] = item_options
        publish_data['selected_items'] = selected_items

    def publish(self, publish_data):
        '''Publish or raise exception if not valid.'''
        raise NotImplementedError()

    def get_scene_selection(self):
        '''Return a list of names for scene selection.'''
        raise NotImplementedError()
