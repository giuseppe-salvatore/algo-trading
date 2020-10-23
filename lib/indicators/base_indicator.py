

class Indicator():

    def __init__(self):
        self._short_name = ""
        self._long_name = ""
        self._description = ""
        self._data = None
        self._params = {}

    @property
    def short_name(self):
        return self._short_name

    @short_name.setter
    def short_name(self, val):
        self._short_name = val

    @property
    def long_name(self):
        return self._long_name

    @long_name.setter
    def long_name(self, val):
        self._long_name = val

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, val):
        self._description = val

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, val):
        self._params = val
        self._update_name()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, val):
        self._data = val

    @property
    def indicator_type(self):
        pass

    def _update_name(self):
        pass

    def calculate(self, data):
        pass
