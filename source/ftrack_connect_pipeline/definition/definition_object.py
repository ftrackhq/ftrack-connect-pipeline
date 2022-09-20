# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

import logging
from ftrack_connect_pipeline.constants import asset as asset_const


class DefinitionObject(dict):
    '''Base DccObject class.'''

    # TODO: could be useful to have a unique id for each definition?
    definition_id = None
    '''Definition id used to unique identify definitions. Not implemented yet '''
    # Definie valid categories that can be converted to custom dictionaries
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
        # self.logger = logging.getLogger(
        #     '{0}.{1}'.format(__name__, self.__class__.__name__)
        # )
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
            self._categories[v.category] = v

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

    # @staticmethod
    # def get_category(item, category_type):
    #     print(type(item))
    #     category_items = DefinitionList([])
    #     if issubclass(type(item), dict):
    #         category = item.get('category')
    #         if category:
    #             if category == category_type:
    #                 return item
    #         for value in list(item.values()):
    #             if issubclass(type(value), list):
    #                 for val in value:
    #                     fund_item = DefinitionObject.get_category(val, category_type)
    #                     if fund_item:
    #                         #return fund_item
    #                         category_items.append(fund_item)
    #     if category_items:
    #         return category_items

    def evaluate_item(self, item):
        # Make sure item is converted to custom object if it's from a
        # compatible category
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


class DefinitionList(list):
    # Define valid categories that can be converted to custom dictionaries
    valid_categories = ['step', 'stage', 'plugin']
    category = None

    def __init__(self, iterable):
        # Iterate over all the objects in the given iterable list, and convert
        # them to custom objects if they match a compatible category
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
        # Make sure item is converted to custom object if it's from a
        # compatible category
        if issubclass(type(item), dict):
            category = item.get('category')
            if category:
                if category in self.valid_categories:
                    cls = eval(category.capitalize())
                    item = cls(item)
                    self.category = category
        return item