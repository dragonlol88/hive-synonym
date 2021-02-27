import abc
import typing

from typing import (
    Optional,
    List,
     Dict,
    Union,
    Any,
    Mapping,
    Callable,
)
from .connections import (
    Connection,
    DBConnection,
    ElasticsearchConnection
)
from .model import ModelBase
from .response import Response
from .exceptions import (
    ResponseModelError,
    DBConnectionError,
    DeserializerError,
    ResponseError
)
from pydantic.error_wrappers import ValidationError


class ClientHandler:

    DEFAULT_CONNECTION_CLASS = Connection

    def __init__(self,
                 hosts,
                 connection_class: Optional[Connection] = None,
                 **options):
        self._hosts = hosts
        self._connection_class = connection_class or self.DEFAULT_CONNECTION_CLASS
        self._connection = self._connection_class(self, **options)

    @property
    def hosts(self):
        """
        Host for connecting with target server
        """
        return self._hosts

    def create_session(self):
        raise NotImplementedError

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError

    def perform(self,
                action: str,
                *,
                model: 'MODEL',
                mapping: Dict[str, Mapping],
                relations: Dict[str, Mapping],
                response_model: Optional['Response'] = None,
                is_flush: Optional[bool] = True,
                pre_process: Optional[Callable[..., 'Response']]=None,
                post_process: Optional[Callable[..., 'Response']]=None,
                is_json: Optional[bool]=True,
                **options):

        raise NotImplementedError

    def evoke_failure_response(self, error):
        """
        It generate return response when request is failed
        Returns dictionary which is specified by developer

        :param error:
            Exception instance
        """
        return {'status': 'failure',
                'data': '',
                'message': error.error,
                'details': error.info}

    def evoke_sucess_response(self, response):
        """
        It generate return response when request is success.
        Returns dictionary which is specified by developer

        :param response(list or dict):
            It is responses that has gone through all the process
        """
        return {'status': 'success',
                'data': response,
                'message': '',
                'details': ''}

    def _resolve_response(self, resp):
        raise NotImplementedError


class DBHandler(ClientHandler):
    """
    This cass tansports all request related with the database
    to the connection and deserialize response data and handler error.
    Or The handler provides an interface for all functions to the client
    without being affected by the client.

    :param hosts
        Url in the form of interworking with sqlalchemy databas
        ex)
            'mysql+pymysql://db_user:db_pwd@db_ip/db_name'
    :param connection_class
        Connection class to be linked
    :param options
        Additional arguments
    """
    DEFAULT_CONNECTION_CLASS = DBConnection

    def __init__(self,
                 hosts,
                 connection_class: Optional[Connection] = None,
                 **options):

        connection_class = connection_class or self.DEFAULT_CONNECTION_CLASS
        super().__init__(hosts, connection_class, **options)

    def perform(self,
                action: str,
                *,
                model,
                mapping,
                relations,
                response_model=None,
                is_flush=True,
                response_preprocess=None,
                response_postprocess=None,
                is_json=True,
                **options):
        """
        Method that handles all requests related to the database

        :param action:
            Database action indication. It is can be insert, update, delete, find
            which are matched with sql expression except for find indication.
            It is matched with select
        :param model:
            Database sqlalchemy model
        :param mapping:
            Ditionary of model mapping is composed of model and setting values.
            ex)
                mappings = {model_class:{'field1': value1, 'field2': value2}}
            model_class: <class synonym.model.*>
        :param relations:
            Dictionary of relations to be deserialized.
            Composed of model field, relation class, relation's field
        :param response_model:
            pydantic model. It can convert simply orm responses to dictionary.
        :param is_flush:
            If is_flush is true, result values is applied to sqlalchemy db model.
        :param response_preprocess:
            It is callable object to process sqlalchemy db model before deserializing
            responses. It can be sorting models, selecting specific field in model.
            It provide flexible data processing when it is difficult and ambiguous
            to process in handler
            argument:
                db models instances generated from sqlalchemy
        :param response_postprocess:
            Similar to response_preprocess but it will be applied after deserialize response
            to dictionary
            argument:
                db models instances generated from sqlalchemy
        :param is_json:
            If it is True, response is converted to dictionary format
        :param options:
            Additional arguments for connection methods
        """

        # db connection interface to communicate with database
        # class <synonym.connections.DBconnection>
        conn: DBConnection = self.connection

        # get action from connection, insert, find, delete, update
        action = self._get_action(action, conn)
        try:
            response = action(model, mapping, relations, **options)
            if is_flush:
                conn.flush()

            # Make the success response
            # If error is raised, context change to except clause
            # and make failure reponse
            result = self.make_response(response,
                                        response_model,
                                        response_preprocess,
                                        response_postprocess,
                                        is_json,
                                        **options)

            # If the request is successful, commit the result
            conn.commit()
        except Exception as error:
            """control error"""
            conn.rollback()
            if isinstance(error, DBConnectionError):
                response = error
            else:
                response = DBConnectionError('db Error', error.args[0])
            result = self.evoke_failure_response(response)

        else:

            # whether error is raise or not, connection must be closed
            # when one request is complicated.
            conn.close()

        #Todo log표시 코드 짜기
        return result

    def make_response(self,
                      response,
                      response_model,
                      response_preprocess,
                      response_postprocess,
                      is_json,
                      **options):
        """
        Call the _deserialize_response function and make the
        final response

        :param response:
            db model instances generated from sqlalchemy
        :param response_model:
            pydantic response model. It can be wrapped from typing module.
            It provide compotable function to deserialize orm model instance
        :param response_preprocess:
            refer to perfrom method
        :param response_postprocess
            refer to perform method
        :param is_json:
            refer to perform method
        :param options:
            Additional arguments for connection methods
        :return:
        """
        try:
            response = _deserialize_response(response,
                                             response_model,
                                             response_preprocess,
                                             response_postprocess,
                                             is_json,
                                             **options)
        except Exception as error:
            raise ResponseError(error.error, error.info)

        # If response deserialization is successful, evoke the success response
        result = self.evoke_sucess_response(response)
        return result

    def _get_action(self, action, conn):
        """
        Get action to process request from connection instance.

        :param action:
            refer to perform method
        :param conn:
            instance <synonym.connections.DBconnection>
        """
        if not hasattr(conn, action):
            raise AttributeError
        return getattr(conn, action)

    @property
    def connection(self):
        """
        communication with database
        """
        return self._connection

    def close(self):
        """
        Close session to cut connection down with database
        """
        self._connection.close()


def _deserialize_response(
                      response: Union[ModelBase, List[ModelBase]],
                      response_model: Optional['Response']=None,
                      response_preprocess=None,
                      response_postprocess=None,
                      json=True,
                      **options) -> 'Response':
    """
    Deserialize the response to dictionary structure. Resolve response model
    to pydantic model and wrapping type if wrapped by typing module. And apply
    response_prepocess, response_proprocess when it is specified.
    Raise error when response_prepocess, response_proprocess is not callable
    object and origin type is different with response_model if not wrapped by
    typing modul and response model field name is wrong.

    :param response:
        refer to make_response method
    :param response_model:
        refer to make_response method
    :param response_preprocess:
        refer to make_response method
    :param response_postprocess:
        refer to make_response method
    :param json:
        refer to perform method
    :param options:
        Additional arguments for connection methods
    """

    if not ((isinstance(response_preprocess, Callable) or
             response_preprocess is None) and  \
            (isinstance(response_postprocess, Callable) or
             response_postprocess is None)):
        """ pre_process 와 pro_process는 callable object여야 한다."""
        raise DeserializerError('Function type Error',
                                'pre or post processor must be callable object')

    response_model, origin = _resolve_response_model(response_model)

    # If origin is not None, that is, origin was wrapped by typing module,
    # origin must be the same type with response
    if origin and origin != type(response):
        raise DeserializerError('Response type Error',
                                '%s is different type with %s' % (origin, response))

    try:
        # Pre-process so that it can be applied
        # in response model immediately
        if response_preprocess:
            response = response_preprocess(response, **options)

        # convert to response model
        # It can be converted to dictionary formatting
        response = _apply_response_model(response,
                                         response_model,
                                         origin,
                                         json)
        if response_postprocess:
            response = response_postprocess(response, **options)
    except Exception as e:
        if isinstance(e, ValidationError):
            raise ResponseModelError('%s Model Error' % e.model.__name__, e.json())
        raise ResponseModelError('Response deserializer Error', e.args[0])

    return response


def _resolve_response_model(response_model):
    """
    Resolve pydantic response_model to origin and model.
    origin is wrapping type from typing module. If it is
    not wrraped, return None.
    response model is pure pydantic response model

    :param response_model:
        pydantic response model wrapped by typing module
    """

    # If reponse_model is instance of typing Generic,
    # it was wrapped by typing module
    # so resolve response model into origin and pure pydantic model
    origin = None
    if isinstance(response_model, typing._GenericAlias):
        origin = response_model.__origin__
        response_model = response_model.__args__[0]

    # pure response model must inherit pydantic response base class
    # specified by developer
    if isinstance(response_model, Response):

        raise ResponseModelError

    return response_model, origin


def _apply_response_model(responses,
                          reponse_model,
                          origin,
                          json: Optional[bool]=True):
    """
    Apply sqlalchemy response model to pydantic response model to
    convert to dictionary format in very simple way.
    Return deserialized responses

    :param responses:
        refer to make_response method
    :param reponse_model:
        refer to make_response method
    :param origin:
        wrapping type from typing module, it can be list, dict..
    """
    result = []
    if responses and origin is None and \
            isinstance(responses, list):
        raise Exception

    # If response have a only one result
    if not isinstance(responses, list):
        result = reponse_model.from_orm(responses)
        if json:
            result = result.dict()
        return result

    # If response have multiple results
    for response in responses:
        response = reponse_model.from_orm(response)
        if json:
            response = response.dict()
        result.append(response)

    return result


class ESHandler(ClientHandler):

    DEFAULT_CONNECTION_CLASS = ElasticsearchConnection

    def __init__(self,
                 hosts,
                 connection_class: typing.Optional[Connection] = None,
                 **options):

        connection_class = connection_class or self.DEFAULT_CONNECTION_CLASS
        super().__init__(hosts, connection_class, **options)

    def mapping(self):
        pass

    def session(self):
        return self._connection

    def close(self):
        self._connection.close()

