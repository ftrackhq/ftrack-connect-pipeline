# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import logging


class DefinitionObject(dict):
    '''Base DccObject class.'''

    # TODO: could be useful to have a unique id for each definition?
    definition_id = None
    '''Definition id used to unique identify definitions. Not implemented yet '''

    valid_categories = ['step', 'stage', 'plugin']
    '''Definie valid categories that can be converted to custom dictionaries'''

    _categories = {}
    '''Holds all the custom categories on the current definition'''

    @property
    def steps(self):
        '''
        Returns all the steps in definition
        '''
        return self._categories['step']

    @property
    def stages(self):
        '''
        Returns all the stages in definition
        '''
        return self._categories['stage']

    @property
    def plugins(self):
        '''
        Returns all the plugins in definition
        '''
        return self._categories['plugin']

    def get_by_name(self, name, type_name=None):
        '''
        Returns all the objects with the given *name* in the definition.
        *type_name* can optionally be passed to filter by name and type at the
        same time.
        '''
        results = []
        for k, v in self._categories.items():
            for item in v:
                if issubclass(type(item), dict):
                    if item.get('name') == name:
                        if not type_name:
                            results.append(item)
                            continue
                        if item.get('type') == type_name:
                            results.append(item)
        return results

    def get_by_type(self, type_name):
        '''
        Returns all the objects with the given *type_name* in the definition.
        '''
        results = []
        for k, v in self._categories.items():
            for item in v:
                if issubclass(type(item), dict):
                    if item.get('type') == type_name:
                        results.append(item)
        return results

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value

    def __init__(self, definition, **kwargs):
        '''
        Convert the given definition to a DefinitionObject
        '''
        super(DefinitionObject, self).__init__({}, **kwargs)
        for key, value in definition.items():
            self[key] = value

    def __getitem__(self, k):
        '''
        Get the value from the given *k*
        '''

        value = super(DefinitionObject, self).__getitem__(k)
        return value

    def __setitem__(self, k, v):
        '''
        Sets the given *v* into the given *k*
        '''
        # If list convert to definition list
        if type(v) == list:
            v = DefinitionList(v)
            # Save and clasify the list object to it's category to quickly query them on the properties
            if v.category in list(self._categories.keys()):
                self._categories[v.category].extend(v)
            else:
                self._categories[v.category] = [item for item in v]

        # If dictionary and valid category, convert to category object
        elif issubclass(type(v), dict):
            v = self.evaluate_item(v)
        super(DefinitionObject, self).__setitem__(k, v)

    def get(self, k, default=None):
        '''
        If exists, returns the value of the given *k* otherwise returns
        *default*.

        *k* : Key of the current dictionary.

        *default* : Default value of the given Key.
        '''
        value = super(DefinitionObject, self).get(k, default)
        return value

    def update(self, *args, **kwargs):
        '''
        Updates the current keys and values with the given ones.
        '''
        # We override this method to make sure that the values are updated
        # using the __setitem__ method
        if args:
            if len(args) > 1:
                raise TypeError(
                    "update expected at most 1 arguments, "
                    "got %d" % len(args)
                )
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        '''
        Sets a default value for the given key.
        '''
        if key not in self:
            self[key] = value
        return self[key]

    def evaluate_item(self, item):
        '''
        Make sure item is converted to custom object if it's from a
        compatible category
        '''
        if issubclass(type(item), dict):
            category = item.get('category')
            if category:
                if category in self.valid_categories:
                    cls = eval(category.capitalize())
                    item = cls(item)
        return item


class Step(DefinitionObject):
    def __init__(self, step):
        super(Step, self).__init__(step)


class Stage(DefinitionObject):
    def __init__(self, stage):
        super(Stage, self).__init__(stage)


class Plugin(DefinitionObject):

    @property
    def options(self):
        '''
        Returns the attribute objects_loaded of the current
        self :obj:`name`
        '''
        return Options(self.get('options'))

    def __init__(self, plugin):
        super(Plugin, self).__init__(plugin)


class Options(DefinitionObject):

    def __init__(self, options):
        super(Options, self).__init__(options)


class DefinitionList(list):
    valid_categories = ['step', 'stage', 'plugin']
    '''Definie valid categories that can be converted to custom dictionaries'''

    # We use the category to identify the type of definition list in
    # the definition object
    category = None
    '''Category of the definition list given by the definition'''

    def __init__(self, iterable):
        '''
        Iterate over all the objects in the given *iterable* list, and convert
        them to custom objects if they match a compatible category
        '''
        new_iter = []
        for item in iterable:
            # evaluate item before assign it
            item = self.evaluate_item(item)
            new_iter.append(item)
        super(DefinitionList, self).__init__(new_iter)

    def __setitem__(self, index, item):
        # evaluate item before assign it
        item = self.evaluate_item(item)
        super(DefinitionList, self).__setitem__(index, item)

    def insert(self, index, item):
        # evaluate item before assign it
        item = self.evaluate_item(item)
        super(DefinitionList, self).insert(index, item)

    def append(self, item):
        # evaluate item before assign it
        item = self.evaluate_item(item)
        super(DefinitionList, self).append(item)

    def extend(self, items):
        new_iter = []
        for item in items:
            # evaluate item before assign it
            item = self.evaluate_item(item)
            new_iter.append(item)
        super(DefinitionList, self).extend(new_iter)

    def evaluate_item(self, item):
        '''
        Make sure item is converted to custom object if it's from a
        compatible category
        '''
        if issubclass(type(item), dict):
            category = item.get('category')
            if category:
                if category in self.valid_categories:
                    cls = eval(category.capitalize())
                    item = cls(item)
                    # Set up the category of the list
                    self.category = category
        return item




'''
Test:
from ftrack_connect_pipeline.definition import definition_object
definition = {'type': 'publisher', 'name': 'File Publisher', 'asset_type': 'scene', 'task_type': 'animation', 'host_type': 'python', 'ui_type': '', 'discoverable': ['Task'], 'contexts': [{'category': 'step', 'type': 'context', 'name': 'main', 'optional': False, 'enabled': True, 'selected': True, 'stages': [{'category': 'stage', 'type': 'context', 'visible': True, 'name': 'context', 'plugins': [{'category': 'plugin', 'type': 'context', 'name': 'context selector', 'plugin': 'common_default_publisher_context', 'widget': 'common_default_publisher_context', 'visible': True, 'editable': True, 'options': {'context_id': '15b346c0-022e-11ea-bc02-ae185fc6f561', 'asset_name': 'testFromPythonConsole', 'comment': 'Nothing to comment', 'status_id': '44dd9fb2-4164-11df-9218-0019bb4983d8'}, 'default_method': 'run'}]}], 'stage_order': ['context']}], 'components': [{'category': 'step', 'type': 'component', 'name': 'main', 'optional': False, 'enabled': True, 'selected': True, 'stages': [{'category': 'stage', 'type': 'collector', 'visible': True, 'name': 'collector', 'plugins': [{'category': 'plugin', 'type': 'collector', 'name': 'collect from given path', 'plugin': 'common_default_publisher_collector', 'widget': 'common_default_publisher_collector', 'visible': True, 'editable': True, 'options': {'path': '/Users/ftrack/Desktop/Screenshot 2022-03-24 at 12.19.03.png'}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'validator', 'visible': True, 'name': 'validator', 'plugins': [{'category': 'plugin', 'type': 'validator', 'name': 'file exists', 'plugin': 'common_file_exists_publisher_validator', 'visible': True, 'editable': True, 'options': {}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'exporter', 'visible': True, 'name': 'exporter', 'plugins': [{'category': 'plugin', 'type': 'exporter', 'name': 'passthrough exporter', 'plugin': 'common_passthrough_publisher_exporter', 'visible': True, 'editable': True, 'options': {}, 'default_method': 'run'}]}], 'stage_order': ['collector', 'validator', 'exporter']}, {'category': 'step', 'type': 'component', 'name': 'thumbnail', 'optional': True, 'enabled': True, 'selected': True, 'stages': [{'category': 'stage', 'type': 'collector', 'visible': True, 'name': 'collector', 'plugins': [{'category': 'plugin', 'type': 'collector', 'name': 'collect from given path', 'plugin': 'common_default_publisher_collector', 'widget': 'common_default_publisher_collector', 'visible': True, 'editable': True, 'options': {'path': '/Users/ftrack/Desktop/Screenshot 2022-03-24 at 12.19.03.png'}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'validator', 'visible': True, 'name': 'validator', 'plugins': [{'category': 'plugin', 'type': 'validator', 'name': 'file exists', 'plugin': 'common_file_exists_publisher_validator', 'visible': True, 'editable': True, 'options': {}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'exporter', 'visible': True, 'name': 'exporter', 'plugins': [{'category': 'plugin', 'type': 'exporter', 'name': 'passthrough exporter', 'plugin': 'common_passthrough_publisher_exporter', 'visible': True, 'editable': True, 'options': {}, 'default_method': 'run'}]}], 'stage_order': ['collector', 'validator', 'exporter']}], 'finalizers': [{'category': 'step', 'type': 'finalizer', 'name': 'main', 'optional': False, 'enabled': True, 'selected': True, 'stages': [{'category': 'stage', 'type': 'pre_finalizer', 'visible': True, 'name': 'pre_finalizer', 'plugins': [{'category': 'plugin', 'type': 'pre_finalizer', 'name': 'pre to ftrack server', 'plugin': 'common_default_publisher_pre_finalizer', 'visible': False, 'editable': True, 'options': {}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'finalizer', 'visible': True, 'name': 'finalizer', 'plugins': [{'category': 'plugin', 'type': 'finalizer', 'name': 'to ftrack server', 'plugin': 'common_default_publisher_finalizer', 'visible': False, 'editable': True, 'options': {}, 'default_method': 'run'}]}, {'category': 'stage', 'type': 'post_finalizer', 'visible': True, 'name': 'post_finalizer', 'plugins': [{'category': 'plugin', 'type': 'post_finalizer', 'name': 'post to ftrack server', 'plugin': 'common_default_publisher_post_finalizer', 'visible': False, 'editable': True, 'options': {}, 'default_method': 'run'}]}], 'stage_order': ['pre_finalizer', 'finalizer', 'post_finalizer']}], '_config': {'type': 'config', 'engine_type': 'publisher'}}
def_object = definition_object.DefinitionObject(definition)
steps = def_object.steps
plugin = steps[0].stages[0].plugins[0]
options = plugin.options
options.test
options.keys()
options.asset_name
options.asset_name = 'testing'


#doing it by our custom class the dictionary is not muttable
from ftrack_connect_pipeline.definition import definition_object
a = {'a': 1, 'context':[{'category':'step', 'info': [{'category':'stage','info': [{'a': 4}]}]}]}
tt = definition_object.DefinitionObject(a)
st = tt.steps[0]
st['info']='qwe'
tt


#Doing it manually the dictionary is mutable
a = {'a': 1, 'context':[{'category':'step', 'info': [{'category':'stage','info': [{'a': 4}]}]}]}
b = a['context'][0]
b['info']='qwe'
a
-'''