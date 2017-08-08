import os

class NotExitingDefault:
    def __str__(self):
        return '(no default)'

class Parameter(object):
    type = 'base_parameter'
    def __init__(self, default=NotExitingDefault()):
        self.default = default

    def __str__(self):
        return '[PARAMETER:: type=%s default=%s]' % (self.type, self.default)

    def as_json(self):
        r = {'type':self.type}
        if not isinstance(self.default, NotExitingDefault):
            r['default'] = self.default
        return r

class StringParameter(Parameter):
    type = 'string'
    def __init__(self, default=NotExitingDefault()):
        super(StringParameter, self).__init__(default=default)
        
class BoolParameter(Parameter):
    type = 'bool'
    def __init__(self, default=NotExitingDefault()):
        super(BoolParameter, self).__init__(default=default)


class IntParameter(Parameter):
    type = 'int'
    def __init__(self, default=NotExitingDefault()):
        super(IntParameter, self).__init__(default=default)


class FloatParameter(Parameter):
    type = 'float'
    def __init__(self, default=NotExitingDefault()):
        super(FloatParameter, self).__init__(default=default)


class StringListParameter(Parameter):
    type = 'string_list'
    def __init__(self, default=NotExitingDefault()):
        super(StringListParameter, self).__init__(default=default)
