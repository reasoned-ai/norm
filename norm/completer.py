from os import listdir
from os.path import isfile, isdir, join
from typing import Dict, List
import logging
logger = logging.getLogger('norm.completer')


def hint_directory(prefix: str) -> List[Dict]:
    logger.debug(prefix)
    parts = prefix.split('"')
    if len(parts) == 1:
        parts = prefix.split("'")
    if len(parts) == 1:
        return []
    logger.debug(f'parts={parts}')
    paths = parts[-1].split('/')
    logger.debug(f'paths={paths}')
    if len(paths) == 1:
        return []
    for i in reversed(range(1, len(paths) + 1)):
        path_prefix = '/'.join(paths[:i])
        logger.debug(path_prefix)
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

