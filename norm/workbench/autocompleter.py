import os
from os import listdir, getcwd
from os.path import isfile, isdir, join
from typing import Dict, List, Optional
import logging
logger = logging.getLogger('auto-completer')


class CompleterResult(object):

    def __init__(self, name: str, value: str, meta: str, score: int):
        self.name: str = name
        self.value: str = value
        self.meta: str = meta
        self.score: int = score

    @property
    def json(self) -> Dict:
        return dict(name=self.name,
                    value=self.value,
                    meta=self.meta,
                    score=self.score)


def hint_directory(prefix: str) -> List[Dict]:
    parts = prefix.split('"')
    if len(parts) == 1:
        parts = prefix.split("'")
    if len(parts) == 1:
        return []
    paths = parts[-1].split('/')
    if len(paths) == 1:
        return []
    for i in reversed(range(1, len(paths) + 1)):
        path_prefix = '/'.join(paths[:i])
        if isdir(path_prefix):
            results = []
            for f in listdir(path_prefix):
                if isfile(join(path_prefix, f)):
                    results.append(dict(name=f, value=f, meta='file', score=100))
                elif isdir(join(path_prefix, f)):
                    results.append(dict(name=f, value=f, meta='folder', score=100))
            return results
    return []


def complete(prefix: str) -> List[Dict]:
    results = hint_directory(prefix)
    return results

