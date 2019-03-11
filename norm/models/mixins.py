from sqlalchemy import Column, Integer, String, Text, exists, and_, TypeDecorator

import json
import logging
import traceback
logger = logging.getLogger(__name__)


def lazy_property(f):
    internal_property = '__lazy_' + f.__name__

    @property
    def lazy_property_wrapper(self):
        try:
            return getattr(self, internal_property)
        except AttributeError:
            v = f(self)
            setattr(self, internal_property, v)
            return v
        except Exception as e:
            raise e
    return lazy_property_wrapper


class LazyMixin(object):
    def invalidate(self, property_name=None):
        """
        Invalidate a lazy property or all lazy properties in the object. If the lazy property does not exist,
        raise AttributeError.
        :param property_name: a lazy property
        :type property_name: str
        :raise: AttributeError
        """
        if property_name is None:
            lazy_properties = (name for name in dir(self) if name.startswith('__lazy_'))
            for p in lazy_properties:
                delattr(self, p)
        else:
            lazy_property_name = '__lazy_' + property_name
            if hasattr(self, lazy_property_name):
                delattr(self, lazy_property_name)


class register_parameter(object):
    PARAMETER_REGISTRY = '__parameter_defaults__'

    def __init__(self, section='main', name='', default='', parameter_type=None, description='', target_class=None):
        self.section = section
        self.name = name
        self.default = default
        if parameter_type is None:
            self.parameter_type = type(default)
        else:
            self.parameter_type = parameter_type
        self.description = description
        self.target_class = target_class

    def __call__(self, cls):
        if self.target_class is not None:
            tcls = self.target_class
        else:
            tcls = cls
        section = cls.__name__ + ':' + self.section
        field = '{}{}'.format(self.PARAMETER_REGISTRY, tcls.__name__)

        if not hasattr(tcls, field):
            # TODO:  decide whether should use dir(cls) or dir(tcls)
            parent_fields = [field for field in dir(cls) if field.startswith(register_parameter.PARAMETER_REGISTRY)]
            parent_param_names = set()
            parent_params = []
            for f in parent_fields:
                p_params=getattr(cls, f)
                # use append then sum should be faster if the loop is deep.  Otherwise, extend should be fast.
                parent_params.append([p for p in p_params if p['name'] not in parent_param_names])
                parent_param_names |= {p['name'] for p in p_params}
            parent_params=sum(parent_params, [])

            setattr(tcls, field, parent_params)
        params = getattr(tcls, field)
        found = [p for p in params if p['name'] == self.name]
        if found:
            msg = 'Parameter {} already defined in class {}'.format(self.name, found[0]['cls'])
            logger.error(msg)
            logger.debug(traceback.print_exc())
            raise ValueError(msg)
        params.append({'section': section,
                       'name': self.name,
                       'default': self.default,
                       'type': self.parameter_type,
                       'description': self.description,
                       'cls': tcls.__name__})
        return cls


class ParametrizedMixin(LazyMixin):
    params = Column(Text, default='{}')

    @lazy_property
    def parameters(self):
        if not self.params or self.params == '':
            return {}

        try:
            return json.loads(self.params)
        except:
            msg = 'Parameters {} can not be parsed as json'.format(self.params)
            logger.error(msg)
            logger.debug(traceback.print_exc())
            raise ValueError(msg)

    @classmethod
    def registered_parameters(cls):
        field = '{}{}'.format(register_parameter.PARAMETER_REGISTRY, cls.__name__)
        if not hasattr(cls, field):
            parent_fields = [field for field in dir(cls) if field.startswith(register_parameter.PARAMETER_REGISTRY)]
            parent_param_names = set()
            parent_params = sum([[p for p in getattr(cls, f) if p['name'] not in parent_param_names]
                                for f in parent_fields], [])
            setattr(cls, field, parent_params)
        return getattr(cls, field)

    @classmethod
    def parameter_default(cls, name):
        """
        Get the default value for a parameter
        :param name: the name of the parameter
        :type name: str
        :return: the default value registered
        """
        for p in cls.registered_parameters():
            if p['name'] == name:
                return p['default']
        return None

    @classmethod
    def parameter_type(cls, name):
        """
        Get the type for a parameter
        :param name: the name of the parameter
        :type name: str
        :return: the type registered
        """
        for p in cls.registered_parameters():
            if p['name'] == name:
                return p['type']
        return None

    @classmethod
    def df_registered_parameters(cls, section=None):
        from pandas import DataFrame
        df = DataFrame(cls.registered_parameters())
        if section is None:
            return df
        else:
            return df.query('section=="{}"'.format(section))

    @classmethod
    def json_registered_parameters(cls, section=None):
        from pandas import DataFrame
        df = DataFrame(cls.registered_parameters())
        if df.empty:
            return '[]'

        df = df[['section', 'name', 'description', 'default']]
        if section is None:
            return df.to_json(orient='records')
        else:
            return df.query('section=="{}"'.format(section)).to_json(orient='records')

    @classmethod
    def markup_registered_parameters(cls, section=None):
        rp = cls.registered_parameters()
        if rp is None or len(rp) == 0:
            return "[]"

        html = "<table width=90%><tr><th>Section</th><th>Name</th><th>Default</th><th>Description</th></tr>"
        for row in rp:
            if section is None or row['section'] == section:
                html += "<tr><td>{}&nbsp;&nbsp;&nbsp;</td><td>{}&nbsp;&nbsp;&nbsp;</td><td>{}&nbsp;&nbsp;&nbsp;</td>" \
                        "<td>{}&nbsp;&nbsp;&nbsp;</td></tr>"\
                    .format(row['section'], row['name'], row['default'], row['description'])
        html += "</table>"
        return html

    def get(self, name, default=None):
        """
        Get the value for a parameter by name
        :param name: the name of the parameter
        :type name: str
        :param default: a given overridden default value
        :return: the value
        """
        return self.parameters.get(name, default or self.parameter_default(name))

    def set(self, name, value):
        """
        Set the value for a parameter
        :param name: the name of the parameter
        :type name: str
        :param value: the value to set
        :return: self
        """
        registered_type = self.parameter_type(name)
        if registered_type is None:
            msg = 'Parameter {} is not registered for class {}'.format(name, self.__class__.__name__)
            logger.error(msg)
            logger.debug(traceback.print_exc())
            raise ValueError(msg)
        if not isinstance(value, registered_type) and not isinstance(registered_type, type(None)):
            msg = 'The value {} is not the same type as registered {}'.format(value, registered_type)
            logger.error(msg)
            logger.debug(traceback.print_exc())
            raise ValueError(msg)
        self.parameters[name] = value
        self.invalidate(name)
        self.params = json.dumps(self.parameters)
        return self


class ARRAY(TypeDecorator):
    """ Sqlite-like does not support arrays.
        Let's use a custom type decorator.

        See http://docs.sqlalchemy.org/en/latest/core/types.html#sqlalchemy.types.TypeDecorator
    """

    impl = String

    def __init__(self, intern=None):
        super().__init__()
        self.intern = intern

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        return json.loads(value)

    def copy(self):
        return ARRAY(self.impl.length)

