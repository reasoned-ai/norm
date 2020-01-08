from sqlalchemy.ext.declarative import declarative_base

import logging
logger = logging.getLogger(__name__)

Model = declarative_base()


class Store(object):
    SEPARATOR = '.'

    def __init__(self, path=''):
        _items = {}
        self.current_path = path

    def __dir__(self):
        return list(self._items.keys())

    def __getattr__(self, item):
        p = self.current_path + self.SEPARATOR + item
        if p in self._items:
            return self._items[p]
        else:
            s = Store(p)
            self._items[p] = s
            return s

    @property
    def latest(self):
        # Retrieve the item according to the path, always the latest version
        return None

    def version(self, ver):
        # Retrieve the item according to the path with the given version
        return None


store = Store()


