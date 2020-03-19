import logging

from IPython import get_ipython
from IPython.core.magic import register_line_cell_magic

from norm.utils import random_name, new_version

logger = logging.getLogger(__name__)

# IPython magics
if get_ipython() is not None:
    ip = get_ipython()
    # TODO use ipython notebook name as the module name
    context = {'module_name': random_name()}

    def init_context():
        context.clear()
        context['module_name'] = random_name()

    @register_line_cell_magic
    def norma(line, cell=None):
        """
        Parsing the norm command and execute it
        :param line: a line of norm command
        :type line: str
        :param cell: a multi-line of norm command
        :type cell: str
        """
        from norm.engine import execute
        module_name = context.get('module_name')
        script = cell or line
        return execute(script, module_name, ip.user_global_ns)
