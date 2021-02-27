from typing import (
    Optional,
    List,
    Tuple,
    Dict,
    Union,
    Any,
    Mapping
)
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy_pagination import paginate

from elasticsearch import Elasticsearch

from .exceptions import (
    DBConnectionError,
    DBFieldTypeError,
    FilterError,
    OrderByError,
    UpdateError,
    DeleteError
)
from .utils import make_one_by_one


def has_iterable(fields):
    for _, v in fields.items():
        if isinstance(v, (list, tuple, set)):
            return True


class Connection:

    def __init__(self,
                 handler,
                 **options):
        # class <synonym.handler.*Handler>
        self.handler = handler

        # Additional arguments
        self.options = options

    def connection(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def insert(self,
             model: 'MODEL',
             mapping: Dict['MODEL', Mapping],
             relations:  Dict[str, Dict['MODEL', Mapping]],
             filter: Union[List[Any], Any],
             order_by: List[Any],
             **options):
        raise NotImplementedError

    def bulk_insert(self,
                    model: 'MODEL',
                    mapping: Dict['MODEL', Mapping],
                    relations:  Dict[str, Dict['MODEL', Mapping]],
                    filter: Union[List[Any], Any],
                    order_by: List[Any],
                    **options):
        raise NotImplementedError

    def find(self,
             model: 'MODEL',
             mapping: Dict['MODEL', Mapping],
             relations:  Dict[str, Dict['MODEL', Mapping]],
             filter: Union[List[Any], Any],
             order_by: List[Any],
             **options):
        raise NotImplementedError

    def update(self,
               model: 'MODEL',
               mapping: Dict['MODEL', Mapping],
               relations:  Dict[str, Dict['MODEL', Mapping]],
               filter: Union[List[Any], Any],
               order_by: List[Any],
               **options):
        raise NotImplementedError

    def delete(self,
               model: 'MODEL',
               mapping: Dict['MODEL', Mapping],
               relations:  Dict[str, Dict['MODEL', Mapping]],
               filter: Union[List[Any], Any],
               order_by: List[Any],
               **options):
        raise NotImplementedError


class DBConnection(Connection):
    """
    This class is just implementer of sqlalchemy orm. It doesn't
    process data response but convey response to the handler.
    Because the database dependecies with handler is broken, connection
    does not affected from the handler. Or DBconnection provide the interface
    for the handler to handle database.

    """
    def __init__(self,
                 handler,
                 **options):
        super().__init__(handler, **options)

        # Create session to communicate with database.
        # And it is primary interface for persistence operations
        self.create_session()

    def insert(self, model, mappings, relations, filter, order_by, **options):
        """
        Method for inserting item in table. Returns response db model set by user
        and raise error when field type is different.

        :param model:
            target model
        :param mapping:
            Ditionary of model mapping is composed of model and setting values.
            ex)
                mappings = {model_class:{'field1': value1, 'field2': value2}}
            model_class: <class synonym.model.*>
        :param relations:
            Dictionary of relations to be deserialized.
            Composed of model field, relation class, relation's field
            ex)
                relations = {
                        'model_field1': {
                            relation_class1:{
                                        field1: value1,
                                        field2: value2
                                    }
                            },
                            .
                            .
                            .
                        }
                relation_class1: <class synonym.model.*>
        :param options:
            Additional arguments for connection methods
        """
        # resolve mapping values to tuple for applying insert
        model, fields = as_tuple(mappings)

        try:
            # objectify database model
            model_inst = _objectify_model(model, fields)

            if relations:
                relation = _objectify_relation_model(model_inst, relations)
        except Exception as e:

            # Check the key of fields or Check Database model attribute
            # if error is raised in this part
            if isinstance(e, (TypeError, AttributeError)):
                raise DBFieldTypeError(
                            "Cant not objective %s" % (model),
                             e.args[0])

            raise DBConnectionError("N/A", e.args[0])

        self.session.add(model_inst)
        return model_inst

    def bulk_insert(self, model, mappings, relations, filter, order_by, **options):
        """
        Method for inserting item in table in bulk way. Returns response db models
        set by user and raise error when field type is different.
        This method is simply executes single insert method multiple times

        :param model:
            target model
        :param mapping:
            List of ditionary of model mapping is composed of model and setting values.
            ex)
                mappings = [{model_class:{'field1': value1, 'field2': value2}}, ...]
            model_class:
                <class synonym.model.*>
        :param relations:
            List of dictionary of relations to be deserialized.
            Composed of model field, relation class, relation's field
            ex)
                relations = [{
                        'model_field1': {
                            relation_class1:{
                                        field1: value1,
                                        field2: value2
                                    }
                            },
                            .
                            .
                            .
                        },
                        .
                        .
                        .]
        :param options:
            Additional arguments for connection methods
        """

        model_lst = []
        for mapping, relation in zip(mappings, relations):
            model_inst = self.insert(model,
                                     mapping,
                                     relation,
                                     **options)
            model_lst.append(model_inst)

        return model_lst

    def find(self, model, mappings, relations, filter, order_by, **options):
        """
        Method for finding item in table. Returns response db models
        set by user and raise error when filter and order_by are improperly
        specified.

        :param model:
            target model for finding items
        :param mappings:
            refer to above function
        :param relations:
            refer to above function
        :param filter:
            List of sqlalchemy filter object for apply to model.
            It is the same with where clause in sql expression
            ex)
                filter = [model.field1 == 'value1',model.like(%value2%), ...]
        :param order_by:
            List of sqlalchemy order by object for apply to model.
            It is asc or desc and same with order_by clause in sql expression
            ex)
                order_by = [desc(model.field1), asc(model.field2)]
        :param options:
            Additional arguments for connection methods.
            page(int): when pagenation is applied, indicating the number of pages
            size(int): How many items should appear per page
        """

        # page = options.pop('page')
        # size = options.pop('size')
        self.query = self.session.query(model)

        try:
            query = self._apply_filter(filter)

            try:
                query = self._apply_order_by(order_by)

            except Exception as e:
                raise OrderByError("order by is improperly made", e.args[0])
        except Exception as e:
            raise FilterError("Filter is improperly made", e.args[0])

        #Todo pagenation 코드 짜기
        # if page and size:
        #     pages = paginate(query, page, size)

        response = query.all()
        return response

    def update(self, model, mappings, relations, filter, order_by, **options):
        """
        Method for updating item in table. Returns response db models
        set by user and raise error when filter are improperly
        specified or when update item type is not properly specified
        """
        self.query = self.session.query(model)
        #filter 적용

        try:
            # apply filter
            query = self._apply_filter(filter)

            # get reponse model instances
            response = query.all()

            # resolve mapping values to tuple for applying update
            _, fields = as_tuple(mappings)
            try:
                response = update_items(response, fields)

            except Exception as e:
                raise UpdateError('Can not be updated', e.args[0])
        except Exception as e:
            raise DBConnectionError("Filter is improperly made", e.args[0])

        return response

    def delete(self, model, mappings, relations, filter, order_by, **options):
        """
        Method for delete item in table. Returns response db models
        set by user and raise error when filter are improperly
        specified
        """

        self.query = self.session.query(model)

        try:
            query = self._apply_filter(filter)
            responses = query.all()
            try:
                for query in responses:
                    self.session.delete(query)
            except Exception as e:
                raise DeleteError("Can not be deleted", e.args[0])
        except Exception as e:
            raise DBConnectionError("DB error", e.args[0])

        return responses

    def _apply_filter(self, filter):
        """
        It is simply applying filter to sqlalchemy object

        :param query: query object to apply
        :param filter: filter parameter

            ex)
            filter = [model.field1 == 'value1',model.like(%value2%), ...]
        """
        #If filter is not specified, return initial query
        if not filter:
            return self.query

        if not isinstance(filter, list):
            filter = [filter]

        return self.query.filter(*filter)

    def _apply_order_by(self,  order_by):
        """
        It is simply applying order_by to sqlalchemy object

        :param query: query object to apply
        :param order_by: order by parameter,
            ex)
                order_by = [desc(model.field1), asc(model.field2)]
        """
        #Skip the order by query, if order by is None
        if not order_by:
            return self.query

        # apply order by
        return self.query.order_by(*order_by)



    def create_session(self, bind=None):

        if bind is None:
            bind = self._create_engine()

        self._session = Session(bind=bind)

    @property
    def session(self) -> Session:
        """
        Connection channel to communicate with database
        """
        return self._session

    def _create_engine(self) -> Engine:
        """
        The Engine is the starting point for any SQLAlchemy application
        """
        return create_engine(self.handler.hosts,
                             echo=False,
                             pool_pre_ping=True,
                             pool_size=50,
                             max_overflow=50)

    def rollback(self):
        """
        Rollback if error is raised from db
        """
        self.session.rollback()

    def flush(self):
        """
        For applying value in db models
        """
        self.session.flush()

    def commit(self):
        """
        Commit for applying result in database
        """
        self.session.commit()

    def close(self):
        """
        Close session to cut connection down with database
        """
        self.session.close()

def as_tuple(models: Dict['MODEL', Mapping]) \
                -> Tuple['MODEL', Mapping]:

    return tuple(models.items())[0]

def _objectify_relation_model(model: 'Model',
                              relations: Dict[str, Dict['MODEL', Mapping]]):
    """
    Funtion to objectify db model by applying field values
    Returns model instances

    :param model:
            Data model instance
    :param relations:
            Dictionary of relations to be deserialized.
            Composed of model field, relation class, relation's field
            ex)
            relations = {
                        'model_field': {
                            relation_class:{
                                        field1: value1,
                                        field2: value2
                                    }
                            }
                        }
            Ways of objectifying relation class
            1. get relation from model getattr(model, relation_field)
            2. objectify relation_class(**{field1: value1, field2: value2})

    """
    for field, mapping in relations.items():

        if not hasattr(model, field):
            raise AttributeError

        relation = getattr(model, field)
        relation_model, fields = as_tuple(mapping)

        # If relation fields has iterable type(list, tuple, set) field
        # resolve them one by one
        if has_iterable(fields):
            fields = make_one_by_one(fields)

        if not isinstance(fields, list):
            fields = [fields]

        for rf in fields:
            relation.append(relation_model(**rf))

    return relation


def _objectify_model(model: 'MODEL',
                     field: Dict[str, Any]):
    """
    Funtion to objectify db model by applying field values
    Returns model instance

    :param model:
        target model for objectifying
    :param field:
        Dictionary of fields to be applied to the model

    """
    if not isinstance(field, dict):
        raise TypeError

    return model(**field)


def update_items(response: List['MODEL'],
                 fields: Dict[str, Any]):
    """
    Function to update item found. Return updated response models

    :param response:
        List of db model to be updated
    :param fields:
        Dictionary of field is composed field and its value
        ex)
            fields = {'field1: value1, 'field2': value2,.....}

    """
    if not isinstance(response, list):
        response = [response]

    for rep_model in response:
        for field, value in fields.items():
            setattr(rep_model, field, value)

    return response


class ElasticsearchConnection(Connection):


    def connection(self) -> Elasticsearch:
        pass

    def close(self):
        pass




