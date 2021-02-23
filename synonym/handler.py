import abc
import typing

from .connections import (
    Connection,
    DBConnection,
    ElasticsearchConnection
)
from .model import ModelBase
from .response import Response
from .exceptions import ResponseModelError, ConnectionError, DeserializerError,ResponseError
from pydantic.error_wrappers import ValidationError

class ClientHandler:

    DEFAULT_CONNECTION_CLASS = Connection

    def __init__(self,
                 hosts,
                 connection_class: typing.Optional[Connection] = None,
                 **options):
        self._hosts = hosts
        self._connection_class = connection_class or self.DEFAULT_CONNECTION_CLASS
        self._connection = self._connection_class(self, **options)

    @property
    def hosts(self):
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
                mapping: typing.Dict[str, typing.Any],
                relations: typing.Dict[str, typing.Any],
                response_model: typing.Optional['Response'] = None,
                is_flush: typing.Optional[bool] = True,
                pre_process: typing.Callable[..., 'Response']=None,
                post_process: typing.Callable[..., typing.Any]=None,
                is_json: typing.Optional[bool]=True,
                **options):

        raise NotImplementedError

    def evoke_failure_response(self, error):
        return {'status': 'failure',
                'data': '',
                'message': error.error,
                'details': error.info}

    def evoke_sucess_response(self, response):
        return {'status': 'success',
                'data': response,
                'message': '',
                'details': ''}

    def _resolve_response(self, resp):
        raise NotImplementedError

class DBHandler(ClientHandler):

    DEFAULT_CONNECTION_CLASS = DBConnection

    def __init__(self,
                 hosts,
                 connection_class: typing.Optional[Connection] = None,
                 **options):

        connection_class = connection_class or self.DEFAULT_CONNECTION_CLASS
        super().__init__(hosts, connection_class, **options)

    def perform(self,
                action: str,
                *,
                model: 'MODEL',
                mapping: typing.Dict[str, typing.Any],
                relations: typing.Dict[str, typing.Any],
                response_model: typing.Optional['Response'] = None,
                is_flush: typing.Optional[bool] = True,
                response_preprocess: typing.Callable[..., 'Response'] = None,
                response_postprocess: typing.Callable[..., typing.Any] = None,
                is_json: typing.Optional[bool] = True,
                **options):

        conn: DBConnection = self.connection
        action = self._get_action(action, conn)
        try:
            response = action(model, mapping, relations, **options)
            if is_flush:
                conn.flush()
            result = self.make_response(response,
                                        response_model,
                                        response_preprocess,
                                        response_postprocess,
                                        is_json,
                                        **options)
            conn.commit()
        except Exception as error:
            """control error"""
            conn.rollback()
            if isinstance(error, ConnectionError):
                response = error
            else:
                response = ConnectionError('db Error', error.args[0])
            result = self.evoke_failure_response(response)

        conn.close()
        return result

    def make_response(self,
                      response,
                      response_model,
                      response_preprocess,
                      response_postprocess,
                      is_json,
                      **options):
        try:
            response = self._deserialize_response(response,
                                                  response_model,
                                                  response_preprocess,
                                                  response_postprocess,
                                                  is_json,
                                                  **options)
        except Exception as error:
            raise ResponseError(error.error, error.info)

        result = self.evoke_sucess_response(response)
        return result




    def _deserialize_response(self,
                          response: typing.Union[ModelBase, typing.List[ModelBase]],
                          response_model: typing.Optional['Response']=None,
                          response_preprocess=None,
                          response_postprocess=None,
                          json=True,
                          **options) -> 'Response':


        if not ((isinstance(response_preprocess,typing.Callable) or
                 response_preprocess is None) and  \
                (isinstance(response_postprocess, typing.Callable) or
                 response_postprocess is None)):
            """ pre_process 와 pro_process는 callable object여야 한다."""
            raise DeserializerError('Function type Error',
                                    'pre or post processor must be callable object')

        response_model, origin = self._resolve_response_model(response_model)

        if origin and origin != type(response):
            """origin이 None이 아니라면 reponse모델과 타입이 같이야합"""
            raise DeserializerError('Response type Error',
                                    '%s is different type with %s' % (origin, response))

        try:
            # Pre-process so that it can be applied
            # in response model immediately
            if response_preprocess:
                response = response_preprocess(response, **options)

            # convert to reponse model
            # It can be converted json formatting
            response = self._apply_response_model(response,
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

    def _resolve_response_model(self,
                               response_model):
        # reponse_model이 typing Generic인지 (typing.List 인지 아닌지)
        origin = None
        if isinstance(response_model, typing._GenericAlias):
            origin = response_model.__origin__
            response_model = response_model.__args__[0]

        if isinstance(response_model, Response):
            """response model은 Response를 상속받아야함."""
            raise ResponseModelError

        return response_model, origin


    def _apply_response_model(self,
                              responses,
                              reponse_model,
                              origin,
                              json: typing.Optional[bool]=True):
        """
        기본적인 바로 reponse를 reponse model에 적용할 수 있는 정도의 기능만 구현
        :param reponse:
        :param reponse_model:
        :param origin:
        :return:
        """
        result = []
        if responses and origin is None and \
                isinstance(responses, list):
            raise Exception

        if not isinstance(responses, list):
            result = reponse_model.from_orm(responses)
            if json:
                result = result.dict()
            return result

        for response in responses:
            response = reponse_model.from_orm(response)
            if json:
                response = response.dict()
            result.append(response)

        return result

    def _get_action(self, action, conn):

        if not hasattr(conn, action):
            raise AttributeError
        return getattr(conn, action)

    @property
    def connection(self):
        return self._connection

    def close(self):
        raise self._connection.close()



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



class FileHandler:
    def __init__(self):
        pass