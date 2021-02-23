import typing

from synonym import ORDER

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from elasticsearch import Elasticsearch
from .exceptions import (
    InstanciateError,
    ImproperlyDataStructureError,
    FilterError,
    OrderByError,
    UpdateError
)

def is_many(fields):
    for _, v in fields.items():
        if isinstance(v, (list, tuple, set)):
            return True

class Connection:

    def __init__(self,
                 handler,
                 **options):
        self.handler = handler
        self.options = options

    def connection(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def insert(self, model, mapping, rels, **options):
        raise NotImplementedError

    def find(self, model, mapping, relations, filter, order_by, **options):
        raise NotImplementedError

    def update(self, model, mapping, relations, filter, **options):
        raise NotImplementedError

    def delete(self, model, mapping, relations, filter, **options):
        raise NotImplementedError


class DBConnection(Connection):

    def __init__(self,
                 handler,
                 **options):
        super().__init__(handler, **options)
        self.create_session()

    def insert(self,
               model: 'MODEL',
               mapping: typing.Dict['MODEL', typing.Any],
               rels: typing.Dict[str, typing.Dict['MODEL', typing.Any]],
               **options):

        #insert 맘에 안들어....
        model, fields = self._resolve_mapping(mapping)
        try:
            model_inst = model(**fields)
        except Exception as e:
            """instanciate Error"""
            raise InstanciateError("Cant not Instanciate %s" % (model), e.args[0])

        if rels is not None:
            for rel, rel_cls_ in rels.items():
                rel_attrs = getattr(model_inst, rel)
                rel_cls, rel_fields = self._resolve_mapping(rel_cls_)

                if is_many(rel_fields):
                    rel_fields = self._make_one_to_many(rel_fields)

                try:
                    if not isinstance(rel_fields, list):
                        rel_fields = [rel_fields]

                    for rf in rel_fields:
                        rel_inst = rel_cls(**rf)
                        rel_attrs.append(rel_inst)
                except Exception as e:
                    """instanciate Error"""
                    raise InstanciateError("Cant not Instanciate %s" % (rel_cls), e.args[0])

        self.session.add(model_inst)
        return model_inst

    def find(self, model, mapping, relations, filter, order_by, **options):
        query = self.session.query(model)
        #filter 적용
        if filter is not None:
            try:
                query = self._apply_filter(query, filter)
            except Exception as e:
                raise FilterError("Filter is improperly made", e.args[0])

        #order by 적용
        if order_by:
            try:
                query = self._apply_order_by(query, model, order_by)
            except Exception as e:
                raise OrderByError("Order by is improperly made", e.args[0])

        response = query.all()
        return response

    def update(self, model, mapping, relations, filter, **options):


        query = self.session.query(model)
        #filter 적용
        if filter is not None:
            try:
                query = self._apply_filter(query, filter)
            except Exception as e:
                raise FilterError("Filter is improperly made", e.args[0])

        _, fields = self._resolve_mapping(mapping)
        response = query.all()
        try:
            response = self._update_items(response, fields)
        except Exception as e:
            """update error 
                invalid type 등등"""
            raise UpdateError('Can not be updated', e.args[0])
        return response

    def delete(self, model, mapping, relations, filter, **options):


        query = self.session.query(model)
        #filter 적용
        if filter is not None:
            try:
                query = self._apply_filter(query, filter)
            except Exception as e:
                raise FilterError("Filter is improperly made", e.args[0])

        responses = query.all()
        for query in responses:
            self.session.delete(query)


        return responses


    def _update_items(self,
                      response: typing.List['MODEL'],
                      fields: typing.Dict[str, typing.Any]):
        if not isinstance(response, list):
            response = [response]
        for rep_model in response:
            for field, value in fields.items():
                setattr(rep_model, field, value)
        return response



    def _apply_order_by(self, query, model, order_by):
        if order_by:
            ords = self._make_order_by(model, order_by)
        return query.order_by(*ords)


    def _apply_filter(self, query, filter):
        if isinstance(filter, list):
            query = query.filter(*filter)
        else:
            query = query.filter(filter)
        return query

    def _make_order_by(self, model, order_by):
        ords = []
        for k, ord in order_by.items():
            ord = ORDER[ord]
            ords.append(ord(getattr(model, k)))
        return ords

    def _resolve_mapping(self, models: typing.Dict['MODEL', typing.Any]) \
            -> typing.Tuple['MODEL', typing.Any]:
        return tuple(models.items())[0]


    def _validate_fields(self, fields):
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

    def _make_one_to_many(self, fields):
        result = []
        keys = fields.keys()
        # 필드의 값이 여러개인 경우와 한 개인 경우가 섞여 있을 때
        # 모든 필드가 여러개 값을 같도록 함
        # 한 개인 경우는 같은 값으로 사이즈를 맞춰줌
        # {'a': 'hello', 'b': [1,2,3]}
        # [{'a': 'hello', 'b': 1},{'a': 'hello', 'b': 2}, {'a': 'hello', 'b': 3}]
        size = self._validate_fields(fields)

        for _ in range(size):
            flat_ = {}
            for key in keys:
                fv = fields[key]
                if isinstance(fv, (list, tuple, set)):
                    fv = fv.pop()
                flat_[key] = fv
            result.append(flat_)
        return result

    def create_session(self, bind=None):
        if bind is None:
            bind = self._create_engine()
        self._session = Session(bind=bind)

    @property
    def session(self) -> Session:
        return self._session

    def _create_engine(self) -> Engine:
        return create_engine(self.handler.hosts,
                             echo=False,
                             pool_pre_ping=True,
                             pool_size=50,
                             max_overflow=50)

    def rollback(self):
        self.session.rollback()

    def flush(self):
        self.session.flush()

    def commit(self):
        self.session.commit()

    def close(self):
        self.session.close()



class ElasticsearchConnection(Connection):


    def connection(self) -> Elasticsearch:
        pass

    def close(self):
        pass




