import typing
from functools import wraps
from werkzeug.exceptions import BadRequest
from synonym import MODELS, AND_OR, ORDER
from .exceptions import ImproperlyDataStructureError


def get_info_from_environ(environ, filter):

    info = {}
    for key, value in environ.items():
        if filter(key):
            key = key.lower()
            info[key] = value
    return info


def chk_request_parameter(expression: bool, msg):
    if not expression:
        raise BadRequest(msg)


def is_excel_file(file):
    return hasattr(file, 'content_type') \
           and file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def _is_relation(field):
    return hasattr(field, 'entity')


def _get_relation_cls(field):
    return field.entity.class_


def make_one_by_one(fields):
    result = []
    keys = fields.keys()
    # 필드의 값이 여러개인 경우와 한 개인 경우가 섞여 있을 때
    # 모든 필드가 여러개 값을 같도록 함
    # 한 개인 경우는 같은 값으로 사이즈를 맞춰줌
    # {'a': 'hello', 'b': [1,2,3]}
    # [{'a': 'hello', 'b': 1},{'a': 'hello', 'b': 2}, {'a': 'hello', 'b': 3}]
    size = _validate_fields(fields)

    for _ in range(size):
        flat_ = {}
        for key in keys:
            fv = fields[key]
            if isinstance(fv, (list, tuple, set)):
                fv = fv.pop()
            flat_[key] = fv
        result.append(flat_)
    return result


def _validate_fields(fields):
    before_size = 0
    size = 1
    for _, v in fields.items():
        if isinstance(v, (list, tuple, set)):
            size = len(v)

            #모든 리스트는 길이가 같아야함
            # {'a':[1,2,3],'b':[1,2]} -> Error
            if before_size != 0 and size != before_size:
                raise ImproperlyDataStructureError("All listed data size must be the same")
            before_size = size

    return size


def _resolve_param_by_one(model, fds, **params):

    models = {}
    relations = {}
    for fd in fds:
        # Get field value from user input
        value = params.get(fd, None)

        # Raise error, if data model does not field attribute
        if not hasattr(model, fd):
            raise AttributeError('%s does not have %s attribute' % (model, fd))

        field = getattr(model, fd)

        # If field is relation in model, make the relation parameter
        if _is_relation(field):
            relastion_class = _get_relation_cls(field)
            for k, v in params.items():
                if hasattr(relastion_class, k):
                    if fd not in relations :
                        relations[fd] = {relastion_class: {k: v}}
                    else:
                        relations[fd][relastion_class][k] = v
        else:
            if value is None:
                raise ValueError
            if model not in models:
                models[model] = {fd: value}
            else:
                models[model][fd] = value

    return models, relations


def _resolve_params(mn, fds, **params):

    if mn not in MODELS:
        raise KeyError('%s model is not exists' % mn)

    model = MODELS[mn]
    bulk = params.get('bulk', None)

    models = []
    relation   = []

    # If fields is not specified, select all data
    if fds is None:
        return model, models, relation

    if bulk:
        for data in bulk:
            params.update(data)
            ms, rs = _resolve_param_by_one(
                                        model,
                                        fds,
                                        **params)
            models.append(ms)
            relation.append(rs)

    else:
        models, rels = _resolve_param_by_one(
                                        model,
                                        fds,
                                        **params)

    return model, models, relation


def _make_filter(model: 'MODEL',
                  where: typing.List[typing.Union[str, typing.Tuple[str, str]]],
                  **kwargs):
    # If where is not specified, return None
    if not where:
        return None

    and_or = None
    filter = []
    for exp in where:
        # Expression is composed of field and operator(=,!=, like etc..) as tuple
        # or logical operator(and, or) as str
        if isinstance(exp, tuple):
            field, op = exp

            # field must be specified with corresponding value
            # if not , raise value error
            if field not in kwargs:
                raise ValueError

            fv = kwargs[field]  # field value
            mf = getattr(model, field)  # model field

            # on_off is =, != operator
            # If value is True, it represent =
            # If value is False, it represent !=
            if op == 'on_off':
                on_off = kwargs[op]
                is_on = on_off[field]
                if is_on:
                    filter.append(mf == fv)
                else:
                    filter.append(mf != fv)
            else:
                if op == 'like':
                    fv = f'%{fv}%'
                op = getattr(mf, op)
                filter.append(op(fv))
        else:

            # Make filter when logical operator changes
            if and_or and and_or != AND_OR[exp]:
                filter = [and_or(*filter)]
            and_or = AND_OR[exp]
    if and_or:
        filter = and_or(*filter)
    return filter


def _make_order_by(model, order_by, **kwargs):

    if not order_by:
        return order_by

    ords = []
    for k, ord in order_by.items():
        # ord is desc or acs
        ord = ORDER[ord]
        ords.append(ord(getattr(model, k)))

    return ords


def _prepare_interface(model, fields, **kwargs):

    where = kwargs.pop('where', None)
    model, mapping, rels = _resolve_params(model, fields, **kwargs)  # Todo models 다시 이름 짓자....
    if not rels:
        rels = None

    filter = _make_filter(model, where, **kwargs)

    return model, mapping, rels, filter


def db_params(**params):

    def _wrapper(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            kwargs.update(params)
            mn  = kwargs.pop('model', None)
            fds = kwargs.pop('fields', None)

            try:
                interface = _prepare_interface(mn, fds, **kwargs)

            except (KeyError,
                    AttributeError,
                    ValueError) as e:
                """exception 처리 잘하"""
                raise e

            interface, filter = interface[:3], interface[-1]
            if filter is not None:
                kwargs['filter'] = filter

            args += interface
            return f(*args, **kwargs)

        return _wrapped

    return _wrapper
