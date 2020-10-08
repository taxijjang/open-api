class Argument(dict):
    def __init__(self, key, require=True, kind='unit', datatype=str,
                 validtypes=None, castings=None, defaultvalue=None,
                 length=None, enum=None, range=None):
        self.key = key
        self.require = require
        self.kind = kind
        self.datatype = datatype
        self.validtypes = list() if validtypes is None else validtypes
        self.castings = list() if castings is None else castings
        self.defaultvalue = defaultvalue

        kwargs = {
            'key': self.key,
            'require': self.require,
            'kind': self.kind,
            'datatype': self.datatype,
            'validtypes': self.validtypes,
            'castings': self.castings,
            'defaultvalue': self.defaultvalue,
        }
        if length is not None:
            self.validtypes.append('length')
            kwargs['length'] = length

        if enum is not None:
            self.validtypes.append('enum')
            kwargs['enum'] = enum

        if range is not None:
            self.validtypes.append('range')
            kwargs['range'] = range

        super(Argument, self).__init__(**kwargs)
