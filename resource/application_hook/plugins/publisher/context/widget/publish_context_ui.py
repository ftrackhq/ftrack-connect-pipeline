# :coding: utf-8
# :copyright: Copyright (c) 2019 ftrack

from ftrack_connect_pipeline import plugin
from ftrack_connect_pipeline.client.widgets import context as context_widget


class ContextWidget(plugin.ContextWidget):
    plugin_name = 'context.publish'

    def run(self, data=None, name=None, description=None, options=None):
        return context_widget.PublishContextWidget(
            session=self.session, data=data, name=name,
            description=description, options=options
        )


def register(api_object, **kw):
    plugin = ContextWidget()
    plugin.register(api_object)
