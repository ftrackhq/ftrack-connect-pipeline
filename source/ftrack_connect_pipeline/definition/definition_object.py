# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import logging
from ftrack_connect_pipeline.constants import asset as asset_const


class DefinitionObject(dict):
    '''Base DccObject class.'''

    # TODO: could be useful to have a unique id for each definition?
    definition_id = None
    '''Definition id used to unique identify definitions. Not implemented yet '''

    # # TODO: we don't really need this 2 properties.
    # @property
    # def name(self):
    #     '''
    #     Return name of the object
    #     '''
    #     return self.get('name')
    #
    # @property
    # def type(self):
    #     '''
    #     Return name of the object
    #     '''
    #     return self.get('type')

    @property
    def steps(self):
        '''
        Returns the attribute objects_loaded of the current
        self :obj:`name`
        '''
        return [Step(step) for step in self.get_category(self, 'step')]

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value

    def __init__(self, definition, **kwargs):
        '''
        If the *from_id* is provided find an object in the dcc with the given
        *from_id* as assset_info_id.
        If a *name* is provided create a new object in the dcc.
        '''
        self.logger = logging.getLogger(
            '{0}.{1}'.format(__name__, self.__class__.__name__)
        )
        self._name = definition.get('name')
        # self._type = type
        super(DefinitionObject, self).__init__(definition, **kwargs)

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
        # We override this method to make sure that we the values are updated
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

    def get_category(self, item, category_type):
        print(type(item))
        category_items = []
        if issubclass(type(item), dict):
            category = item.get('category')
            if category != None:
                if category == category_type:
                    return item
            for value in list(item.values()):
                if type(value) == list:
                    for val in value:
                        fund_item = self.get_category(val, category_type)
                        if fund_item:
                            #return fund_item
                            category_items.append(fund_item)
        if category_items:
            return category_items


    # def _option_exists(self, name):
    #     '''
    #     Return true if the given *name* exists in the scene.
    #     '''
    #     raise NotImplementedError
    #
    # def from_asset_info_id(self, asset_info_id):
    #     '''
    #     Checks the dcc to get all the ftrack objects. Compares them
    #     with the given *asset_info_id* and returns them if matches.
    #     '''
    #     raise NotImplementedError
    #
    # @staticmethod
    # def dictionary_from_object(object_name):
    #     '''
    #     Static method to be used without initializing the current class.
    #     Returns a dictionary with the keys and values of the given
    #     *object_name* if exists.
    #
    #     *object_name* ftrack object type from the DCC.
    #     '''
    #     raise NotImplementedError
    #
    # def connect_objects(self, objects):
    #     '''
    #     Link the given *objects* ftrack attribute to the self
    #     :obj:`name` object asset_link attribute in the DCC.
    #
    #     *objects* List of DCC objects
    #     '''
    #     raise NotImplementedError
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
'''

class Step(DefinitionObject):

    @property
    def stages(self):
        '''
        Returns the attribute objects_loaded of the current
        self :obj:`name`
        '''
        return [Stage(stage) for stage in self.get_category(self, 'stage')]

    def __init__(self, step):
        super(Step, self).__init__(step)


class Stage(DefinitionObject):

    @property
    def plugins(self):
        '''
        Returns the attribute objects_loaded of the current
        self :obj:`name`
        '''
        return [Plugin(plugin) for plugin in self.get_category(self, 'plugin')]

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

    #TODO: maybe create the options class as well in order to properly
    # augn¡ment the options whichis the important peace.
    #  Is ther a way to convert all the dictonary keys to properties?

class Options(DefinitionObject):

    @property
    def test(self):
        '''
        Returns the attribute objects_loaded of the current
        self :obj:`name`
        '''
        return 'test'
    def __init__(self, options):
        super(Options, self).__init__(options)

    #TODO: maybe create the options class as well in order to properly
    # augn¡ment the options whichis the important peace.
    #  Is ther a way to convert all the dictonary keys to properties?