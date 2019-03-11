from norm.engine import NormCompiler
from norm.config import context_id, session
from norm.security import user

from IPython.core.magic import register_line_magic, register_cell_magic, register_line_cell_magic

import logging
logger = logging.getLogger(__name__)

context = NormCompiler(context_id, user, session)


# IPython magics
@register_line_cell_magic
def norm(line, cell=None):
    """
    Parsing the norm command and execute it
    :param line: a line of norm command
    :type line: str
    :param cell: a multi-line of norm command
    :type cell: str
    """
    if cell is None:
        return context.execute(line)
    else:
        return context.execute(cell)
