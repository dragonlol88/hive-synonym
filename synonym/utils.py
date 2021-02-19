import typing

from functools import wraps
from synonym import MODELS, AND_OR


def _is_rels(field):
    return hasattr(field, 'entity')

def _get_rels_cls(field):
    return field.entity.class_


def _resolve_params(mn, fds, **params):

    if mn not in MODELS:
        raise KeyError('%s model is not exists' % mn)

    model = MODELS[mn]
    models = {}
    rels   = {}

    #field가 정해지지 않음,,해당 테이블의 모든 데이터  조회 하려할 때
    if fds is None:
        return model, models, rels

    for fd in fds:
        origin_param = params.copy()
        #Todo 사용된 parameter가 소비 되지 않는 이슈
        value = params.get(fd, None)
        if not hasattr(model, fd):
            raise AttributeError('%s does not have %s attribute' % (model, fd))

        field = getattr(model, fd)
        if _is_rels(field):
            rels_cls = _get_rels_cls(field)
            for k, v in params.items():
                if hasattr(rels_cls, k):

                    param, value = k, v
                    if fd not in rels:
                        rels[fd] = {rels_cls: {param: value}}
                    else:
                        rels[fd][rels_cls][param] = value
        else:
            if value is None:
                raise ValueError
            if model not in models:
                models[model] = {fd: value}
            else:
                models[model][fd] = value

    return model, models, rels

def _make_fileter(model: 'MODEL',
                  where: typing.List[typing.Union[str, typing.Tuple[str, str]]],
                  **kwargs):
    if where is None:
        return None

    and_or = None
    filter = []
    for exp in where:
        if isinstance(exp, tuple):
            field, op = exp
            if field not in kwargs:
                """field는 있는데 값이 없으면 error"""
                raise ValueError

            fv = kwargs[field]  # field value
            mf = getattr(model, field)  # model field
            if op == 'on_off':

                on_off = kwargs[op]
                is_on = on_off[field]
                if is_on:
                    filter.append(mf == fv)
                else:
                    filter.append(mf != fv)
            else:
                op = getattr(mf, op)
                filter.append(op(fv))
        else:

            if and_or and and_or != AND_OR[exp]:
                filter = [and_or(*filter)]
            and_or = AND_OR[exp]
    if and_or:
        filter = and_or(*filter)
    return filter


def _prepare_interface(model, fields, **kwargs):

    where = kwargs.pop('where', None)
    model, mapping, rels = _resolve_params(model, fields, **kwargs)  # Todo models 다시 이름 짓자....
    if not rels:
        rels = None

    filter = _make_fileter(model, where, **kwargs)

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
