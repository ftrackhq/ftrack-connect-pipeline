# :coding: utf-8
# :copyright: Copyright (c) 2014-2022 ftrack

from collections.abc import MutableMapping


class DefinitionObject(MutableMapping):
    '''Base DccObject class.'''

    # TODO: could be useful to have a unique id for each definition?
    definition_id = None
    '''Definition id used to unique identify definitions. Not implemented yet '''

    valid_categories = ['step', 'stage', 'plugin']
    '''Definie valid categories that can be converted to custom dictionaries'''

    _categories = {}
    '''Holds all the custom categories on the current definition'''

    def get_by_name(self, name, type_name=None):
        '''
        Returns all the objects with the given *name* in the definition.
        *type_name* can optionally be passed to filter by name and type at the
        same time.
        '''
        results = []
        for k, v in self._categories.items():
            for item in v:
                if issubclass(type(item), DefinitionObject):
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
                if issubclass(type(item), DefinitionObject):
                    if item.get('type') == type_name:
                        results.append(item)
        return results

    def get_by_category(self, category_name):
        '''
        Returns all the objects with the given *category_name* in the definition.
        '''
        return self._categories.get(category_name)


    def __init__(self, definition):
        '''
        Convert the given definition to a DefinitionObject
        '''
        super(DefinitionObject, self).__setattr__('mapping', {})
        self.update(definition)

    def __getattr__(self, k):
        return self.mapping[k]

    def __setattr__(self, k, value):
        self.mapping[k] = value

    def __getitem__(self, k):
        '''
        Get the value from the given *k*
        '''

        return self.mapping[k]

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
                self._categories[v.category] = list(item for item in v)

        # If dictionary and valid category, convert to category object
        elif issubclass(type(v), dict):
            v = self.evaluate_item(v)
        self.mapping[k] = v

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

    def __delitem__(self, key):
        del self.mapping[key]

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return f"{type(self).__name__}({self.mapping})"



class Step(DefinitionObject):
    def __init__(self, step):
        super(Step, self).__init__(step)


class Stage(DefinitionObject):
    def __init__(self, stage):
        super(Stage, self).__init__(stage)


class Plugin(DefinitionObject):

    def __init__(self, plugin):
        super(Plugin, self).__init__(plugin)

    def __setitem__(self, k, v):
        '''
        Sets the given *v* into the given *k*
        '''
        # Convert options to options object
        if k == 'options':
            v = Options(v)
        super(Plugin, self).__setitem__(k, v)


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

